"""
RFM segmentation audit — verifies that all five segments are populated
against the seeded OLTP data.

    docker compose run --rm ml python -m src.models.customer_segmentation
"""
from __future__ import annotations

import os
from collections import Counter

from sqlalchemy import create_engine, text


RFM_SQL = """
WITH last_day AS (
    SELECT MAX(sale_date)::date AS d FROM sales
),
customer_rfm AS (
    SELECT
        c.id::text AS customer_id,
        COALESCE((SELECT d FROM last_day) - MAX(s.sale_date)::date, 999999)::int
            AS recency_days,
        COUNT(DISTINCT s.id)::int AS frequency,
        COALESCE(SUM(si.quantity * si.unit_price), 0)::float AS monetary
    FROM customers c
    LEFT JOIN sales s ON s.customer_id = c.id AND s.status <> 'cancelled'
    LEFT JOIN sale_items si ON si.sale_id = s.id
    GROUP BY c.id
),
scored AS (
    SELECT
        customer_id, recency_days, frequency, monetary,
        (6 - NTILE(5) OVER (ORDER BY recency_days ASC))::int AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)::int AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)::int AS m_score
    FROM customer_rfm
)
SELECT
    recency_days, frequency, monetary, r_score, f_score, m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'High Value'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New'
        ELSE 'Inactive'
    END AS segment
FROM scored
"""

REQUIRED = ["High Value", "Loyal", "At Risk", "New", "Inactive"]


def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)

    with engine.connect() as conn:
        rows = conn.execute(text(RFM_SQL)).mappings().all()

    print(f"→ total customers scored: {len(rows)}")
    print()

    counts = Counter(r["segment"] for r in rows)
    total = sum(counts.values()) or 1

    print(f"{'Segment':<14} {'Count':>7} {'Share':>8}  {'Avg R':>7} {'Avg F':>8} {'Avg M':>14}")
    print("-" * 72)
    for seg in REQUIRED:
        items = [r for r in rows if r["segment"] == seg]
        n = len(items)
        share = n / total
        if items:
            avg_r = sum(int(r["recency_days"]) for r in items) / n
            avg_f = sum(int(r["frequency"]) for r in items) / n
            avg_m = sum(float(r["monetary"]) for r in items) / n
            print(f"{seg:<14} {n:>7} {share*100:>7.1f}%  {avg_r:>7.1f} {avg_f:>8.1f} {avg_m:>14,.0f}")
        else:
            print(f"{seg:<14} {0:>7} {0.0:>7.1f}%  {'-':>7} {'-':>8} {'-':>14}")

    print()
    missing = [s for s in REQUIRED if counts[s] == 0]
    if missing:
        print(f"❌ MISSING SEGMENTS: {missing}")
        raise SystemExit(1)

    print("✅ All five segments populated.")


if __name__ == "__main__":
    main()