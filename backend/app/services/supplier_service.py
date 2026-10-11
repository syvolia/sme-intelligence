from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.suppliers import (
    SupplierRow,
    SuppliersResponse,
    SupplierSummary,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


# ---------------------------------------------------------------------------
# OLTP path — aggregates purchase_orders directly
# ---------------------------------------------------------------------------
OLTP_SQL = """
WITH last_day AS (
    SELECT MAX(order_date)::date AS d FROM purchase_orders
),
agg AS (
    SELECT
        s.id::text  AS supplier_id,
        s.name      AS supplier,
        s.country   AS country,
        COUNT(po.id)::int AS orders,
        COUNT(po.received_date)::int AS received_orders,
        COALESCE(
            AVG(EXTRACT(EPOCH FROM (po.received_date - po.order_date)) / 86400.0)
                FILTER (WHERE po.received_date IS NOT NULL),
            0
        )::float AS avg_delivery_days,
        COALESCE(
            AVG(GREATEST(
                EXTRACT(EPOCH FROM (po.received_date - po.expected_date)) / 86400.0,
                0
            )) FILTER (WHERE po.received_date IS NOT NULL),
            0
        )::float AS avg_lateness_days,
        COALESCE(
            COUNT(*) FILTER (WHERE po.received_date <= po.expected_date)::float
                / NULLIF(COUNT(po.received_date), 0),
            0
        )::float AS on_time_pct,
        COALESCE(AVG(po.unit_cost)::float, 0) AS avg_cost,
        COALESCE(SUM(po.quantity * po.unit_cost)::float, 0) AS total_spend
    FROM suppliers s
    LEFT JOIN purchase_orders po ON po.supplier_id = s.id
    GROUP BY s.id, s.name, s.country
),
recent AS (
    SELECT
        po.supplier_id::text AS supplier_id,
        COALESCE(
            COUNT(*) FILTER (WHERE po.received_date <= po.expected_date)::float
                / NULLIF(COUNT(po.received_date), 0),
            0
        )::float AS recent_on_time_pct
    FROM purchase_orders po
    WHERE po.order_date >= (SELECT d - INTERVAL '90 days' FROM last_day)
    GROUP BY po.supplier_id
)
SELECT
    a.supplier_id, a.supplier, a.country,
    a.orders, a.received_orders,
    a.avg_delivery_days, a.avg_lateness_days, a.on_time_pct,
    COALESCE(r.recent_on_time_pct, a.on_time_pct)::float AS recent_on_time_pct,
    a.avg_cost, a.total_spend
FROM agg a
LEFT JOIN recent r ON r.supplier_id = a.supplier_id
"""


# ---------------------------------------------------------------------------
# Warehouse path — reads from fact_purchase_orders joined to dim_supplier
# ---------------------------------------------------------------------------
WAREHOUSE_SQL = """
WITH last_day AS (
    SELECT MAX(order_date)::date AS d FROM {fact_purchase_orders}
),
agg AS (
    SELECT
        s.supplier_id::text                                AS supplier_id,
        s.name                                             AS supplier,
        s.country                                          AS country,
        COUNT(f.po_key)::int                               AS orders,
        COUNT(f.received_date)::int                        AS received_orders,
        COALESCE(AVG(f.lead_time_days) FILTER (WHERE f.lead_time_days IS NOT NULL), 0)::float
                                                           AS avg_delivery_days,
        COALESCE(AVG(GREATEST(
            EXTRACT(EPOCH FROM (f.received_date - f.expected_date)) / 86400.0, 0
        )) FILTER (WHERE f.received_date IS NOT NULL), 0)::float
                                                           AS avg_lateness_days,
        COALESCE(COUNT(*) FILTER (WHERE f.on_time_flag)::float
            / NULLIF(COUNT(f.received_date), 0), 0)::float AS on_time_pct,
        COALESCE(AVG(f.unit_cost)::float, 0)               AS avg_cost,
        COALESCE(SUM(f.total_cost)::float, 0)              AS total_spend
    FROM {dim_supplier} s
    LEFT JOIN {fact_purchase_orders} f ON f.supplier_key = s.supplier_key
    GROUP BY s.supplier_id, s.name, s.country
),
recent AS (
    SELECT
        f.supplier_key,
        COALESCE(COUNT(*) FILTER (WHERE f.on_time_flag)::float
            / NULLIF(COUNT(f.received_date), 0), 0)::float AS recent_on_time_pct
    FROM {fact_purchase_orders} f
    WHERE f.order_date >= (SELECT d - INTERVAL '90 days' FROM last_day)
    GROUP BY f.supplier_key
)
SELECT
    a.supplier_id, a.supplier, a.country,
    a.orders, a.received_orders,
    a.avg_delivery_days, a.avg_lateness_days, a.on_time_pct,
    COALESCE(r.recent_on_time_pct, a.on_time_pct)::float AS recent_on_time_pct,
    a.avg_cost, a.total_spend
FROM agg a
LEFT JOIN {dim_supplier} s ON s.supplier_id = a.supplier_id
LEFT JOIN recent r ON r.supplier_key = s.supplier_key
"""


def _tier(reliability: float) -> str:
    if reliability >= 90:
        return "Excellent"
    if reliability >= 75:
        return "Good"
    if reliability >= 60:
        return "Fair"
    return "Poor"


def _trend(recent: float, overall: float) -> str:
    delta = recent - overall
    if delta < -0.05:
        return "degrading"
    if delta > 0.05:
        return "improving"
    return "stable"


def get_suppliers(db: Session, currency: str = "KES") -> SuppliersResponse:
    if settings.warehouse_enabled:
        sql = WAREHOUSE_SQL.format(
            fact_purchase_orders=_t("fact_purchase_orders"),
            dim_supplier=_t("dim_supplier"),
        )
    else:
        sql = OLTP_SQL

    rows = db.execute(text(sql)).mappings().all()

    suppliers: list[SupplierRow] = []
    for r in rows:
        orders = int(r["orders"] or 0)
        received = int(r["received_orders"] or 0)

        on_time = float(r["on_time_pct"] or 0.0)
        recent = float(r["recent_on_time_pct"] or 0.0)
        lateness_days = float(r["avg_lateness_days"] or 0.0)

        fulfillment_rate = (received / orders) if orders else 0.0
        lateness_score = max(0.0, 1.0 - min(1.0, lateness_days / 7.0))

        reliability = 100.0 * (
            0.60 * on_time
            + 0.25 * fulfillment_rate
            + 0.15 * lateness_score
        )

        suppliers.append(
            SupplierRow(
                supplier_id=r["supplier_id"],
                supplier=r["supplier"],
                country=r["country"],
                orders=orders,
                received_orders=received,
                avg_delivery_days=round(float(r["avg_delivery_days"] or 0.0), 2),
                avg_lateness_days=round(lateness_days, 2),
                on_time_pct=round(on_time, 4),
                recent_on_time_pct=round(recent, 4),
                avg_cost=round(float(r["avg_cost"] or 0.0), 2),
                total_spend=round(float(r["total_spend"] or 0.0), 2),
                reliability=round(reliability, 1),
                trend=_trend(recent, on_time),
                tier=_tier(reliability),
            )
        )

    active = [s for s in suppliers if s.orders >= 3]
    best = max(active, key=lambda s: s.reliability).supplier if active else None
    worst = min(active, key=lambda s: s.reliability).supplier if active else None

    summary = SupplierSummary(
        total_suppliers=len(suppliers),
        avg_reliability=round(
            sum(s.reliability for s in suppliers) / len(suppliers), 1
        ) if suppliers else 0.0,
        avg_on_time_pct=round(
            sum(s.on_time_pct for s in suppliers) / len(suppliers), 4
        ) if suppliers else 0.0,
        best_supplier=best,
        worst_supplier=worst,
        at_risk_count=sum(1 for s in suppliers if s.reliability < 75),
        currency=currency,
    )

    suppliers.sort(key=lambda s: s.reliability)

    return SuppliersResponse(summary=summary, suppliers=suppliers)