from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.customers import (
    CustomerListRow,
    CustomerScatterPoint,
    CustomersResponse,
    CustomerTotals,
    SegmentSummary,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


SEGMENT_ORDER = ["High Value", "Loyal", "At Risk", "New", "Inactive"]


# ---------------------------------------------------------------------------
# OLTP path — computes RFM inline
# ---------------------------------------------------------------------------
OLTP_RFM_SQL = """
WITH last_day AS (
    SELECT MAX(sale_date)::date AS d FROM sales
),
customer_rfm AS (
    SELECT
        c.id::text AS customer_id,
        c.name AS name,
        COALESCE((SELECT d FROM last_day) - MAX(s.sale_date)::date, 999999)::int
            AS recency_days,
        COUNT(DISTINCT s.id)::int AS frequency,
        COALESCE(SUM(si.quantity * si.unit_price), 0)::float AS monetary
    FROM customers c
    LEFT JOIN sales s ON s.customer_id = c.id AND s.status <> 'cancelled'
    LEFT JOIN sale_items si ON si.sale_id = s.id
    GROUP BY c.id, c.name
),
scored AS (
    SELECT
        customer_id, name, recency_days, frequency, monetary,
        (6 - NTILE(5) OVER (ORDER BY recency_days ASC))::int AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)::int          AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)::int           AS m_score
    FROM customer_rfm
)
SELECT
    customer_id, name, recency_days, frequency, monetary,
    r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'High Value'
        WHEN r_score >= 3 AND f_score >= 3                   THEN 'Loyal'
        WHEN r_score <= 2 AND f_score >= 3                   THEN 'At Risk'
        WHEN r_score >= 4 AND f_score <= 2                   THEN 'New'
        ELSE 'Inactive'
    END AS segment
FROM scored
"""


# ---------------------------------------------------------------------------
# Warehouse path — reads from the pre-computed RFM mart
# ---------------------------------------------------------------------------
WAREHOUSE_RFM_SQL = """
SELECT
    customer_id,
    name,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    segment
FROM {mart_customer_rfm}
"""


def get_customers(db: Session, currency: str = "KES") -> CustomersResponse:
    if settings.warehouse_enabled:
        sql = WAREHOUSE_RFM_SQL.format(mart_customer_rfm=_t("mart_customer_rfm"))
    else:
        sql = OLTP_RFM_SQL

    rows = db.execute(text(sql)).mappings().all()

    total = len(rows)
    total_revenue = sum(float(r["monetary"]) for r in rows) or 1.0
    active = sum(1 for r in rows if int(r["recency_days"]) <= 30)
    repeat = sum(1 for r in rows if int(r["frequency"]) >= 2)
    avg_value = (sum(float(r["monetary"]) for r in rows) / total) if total else 0.0

    # ---- per-segment aggregates -----------------------------------------
    buckets: dict[str, list] = {s: [] for s in SEGMENT_ORDER}
    for r in rows:
        buckets[r["segment"]].append(r)

    segments: list[SegmentSummary] = []
    for seg in SEGMENT_ORDER:
        items = buckets[seg]
        if not items:
            segments.append(
                SegmentSummary(
                    segment=seg,
                    count=0,
                    revenue=0.0,
                    revenue_share=0.0,
                    avg_monetary=0.0,
                    avg_frequency=0.0,
                    avg_recency_days=0.0,
                )
            )
            continue

        rev = sum(float(r["monetary"]) for r in items)
        segments.append(
            SegmentSummary(
                segment=seg,
                count=len(items),
                revenue=round(rev, 2),
                revenue_share=round(rev / total_revenue, 4),
                avg_monetary=round(rev / len(items), 2),
                avg_frequency=round(
                    sum(int(r["frequency"]) for r in items) / len(items), 2
                ),
                avg_recency_days=round(
                    sum(int(r["recency_days"]) for r in items) / len(items), 1
                ),
            )
        )

    # ---- scatter points -------------------------------------------------
    scatter = [
        CustomerScatterPoint(
            customer_id=r["customer_id"],
            name=r["name"],
            segment=r["segment"],
            recency_days=int(r["recency_days"]),
            frequency=int(r["frequency"]),
            monetary=round(float(r["monetary"]), 2),
        )
        for r in rows
    ]

    # ---- top 20 by monetary ---------------------------------------------
    top = sorted(rows, key=lambda r: float(r["monetary"]), reverse=True)[:20]
    top_customers = [
        CustomerListRow(
            customer_id=r["customer_id"],
            name=r["name"],
            segment=r["segment"],
            recency_days=int(r["recency_days"]),
            frequency=int(r["frequency"]),
            monetary=round(float(r["monetary"]), 2),
            r_score=int(r["r_score"]),
            f_score=int(r["f_score"]),
            m_score=int(r["m_score"]),
        )
        for r in top
    ]

    return CustomersResponse(
        totals=CustomerTotals(
            total_customers=total,
            active_customers=active,
            repeat_customers=repeat,
            avg_customer_value=round(avg_value, 2),
            currency=currency,
        ),
        segments=segments,
        scatter=scatter,
        top_customers=top_customers,
    )