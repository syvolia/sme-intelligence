"""
Supplier reliability audit — prints each supplier's score and flags the
degrading one.

    docker compose run --rm ml python -m src.models.supplier_audit
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine, text


AGG_SQL = """
WITH last_day AS (SELECT MAX(order_date)::date AS d FROM purchase_orders),
agg AS (
    SELECT
        s.name AS supplier,
        COUNT(po.id)::int AS orders,
        COUNT(po.received_date)::int AS received,
        COALESCE(AVG(EXTRACT(EPOCH FROM (po.received_date - po.order_date)) / 86400.0)
            FILTER (WHERE po.received_date IS NOT NULL), 0)::float AS avg_delivery,
        COALESCE(AVG(GREATEST(EXTRACT(EPOCH FROM (po.received_date - po.expected_date)) / 86400.0, 0))
            FILTER (WHERE po.received_date IS NOT NULL), 0)::float AS avg_lateness,
        COALESCE(COUNT(*) FILTER (WHERE po.received_date <= po.expected_date)::float
            / NULLIF(COUNT(po.received_date), 0), 0)::float AS on_time
    FROM suppliers s
    LEFT JOIN purchase_orders po ON po.supplier_id = s.id
    GROUP BY s.name
),
recent AS (
    SELECT po.supplier_id, 
        COALESCE(COUNT(*) FILTER (WHERE po.received_date <= po.expected_date)::float
            / NULLIF(COUNT(po.received_date), 0), 0)::float AS recent_on_time
    FROM purchase_orders po
    WHERE po.order_date >= (SELECT d - INTERVAL '90 days' FROM last_day)
    GROUP BY po.supplier_id
)
SELECT a.supplier, a.orders, a.received, a.avg_delivery, a.avg_lateness, a.on_time,
       COALESCE(r.recent_on_time, a.on_time)::float AS recent_on_time
FROM agg a
LEFT JOIN recent r ON r.supplier_id = (SELECT id FROM suppliers WHERE name = a.supplier)
ORDER BY a.on_time;
"""


def main() -> None:
    engine = create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        rows = conn.execute(text(AGG_SQL)).mappings().all()

    print(f"{'Supplier':<32} {'Ord':>4} {'Rcvd':>5} {'Deliv':>6} {'Late':>5} {'OnTm':>6} {'Recent':>7} {'Tier':>10} {'Trend':>10}")
    print("-" * 100)

    degrading: list[str] = []
    for r in rows:
        orders = int(r["orders"] or 0)
        received = int(r["received"] or 0)
        on_time = float(r["on_time"] or 0)
        recent = float(r["recent_on_time"] or 0)
        lateness = float(r["avg_lateness"] or 0)

        fulfillment = (received / orders) if orders else 0.0
        lateness_score = max(0.0, 1.0 - min(1.0, lateness / 7.0))
        reliability = 100.0 * (0.60 * on_time + 0.25 * fulfillment + 0.15 * lateness_score)

        tier = "Excellent" if reliability >= 90 else "Good" if reliability >= 75 else "Fair" if reliability >= 60 else "Poor"
        delta = recent - on_time
        trend = "degrading" if delta < -0.05 else "improving" if delta > 0.05 else "stable"

        if trend == "degrading":
            degrading.append(r["supplier"])

        print(
            f"{r['supplier'][:32]:<32} {orders:>4} {received:>5} "
            f"{float(r['avg_delivery']):>6.2f} {lateness:>5.2f} "
            f"{on_time*100:>5.1f}% {recent*100:>6.1f}% "
            f"{reliability:>9.1f} {trend:>10}"
        )

    print()
    if not degrading:
        print("⚠ No degrading supplier detected — the seed pattern may be missing.")
        raise SystemExit(1)

    print(f"✅ Degrading supplier(s): {degrading}")


if __name__ == "__main__":
    main()