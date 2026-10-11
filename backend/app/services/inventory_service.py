from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.inventory import (
    InventoryItem,
    InventoryResponse,
    InventorySummary,
    RiskStatus,
)


def _t(name: str) -> str:
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


# ---------------------------------------------------------------------------
# Risk classification — only used on the OLTP path. On the warehouse path the
# classification is pre-computed in fact_inventory_snapshot.risk.
# ---------------------------------------------------------------------------
def _classify(
    current_stock: int,
    daily_demand: float,
    lead_time_days: int,
    lead_time_demand: float,
    reorder_point: int,
) -> RiskStatus:
    if current_stock <= 0:
        return "CRITICAL"
    if daily_demand > 0 and current_stock <= lead_time_demand:
        return "CRITICAL"
    if current_stock <= reorder_point:
        return "LOW"
    return "HEALTHY"


# ---------------------------------------------------------------------------
# OLTP path — original query, unchanged
# ---------------------------------------------------------------------------
OLTP_SQL = """
WITH last_day AS (
    SELECT MAX(sale_date)::date AS d FROM sales
),
stock AS (
    SELECT branch_id, product_id,
           SUM(CASE WHEN movement_type = 'in'  THEN quantity
                    WHEN movement_type = 'out' THEN -quantity
                    ELSE quantity END)::int AS current_stock
    FROM inventory_movements
    GROUP BY 1, 2
),
demand AS (
    SELECT s.branch_id     AS branch_id,
           si.product_id   AS product_id,
           SUM(si.quantity)::int          AS units_30d,
           SUM(si.quantity)::float / 30.0 AS daily_demand
    FROM sale_items si
    JOIN sales s ON s.id = si.sale_id
    WHERE s.status <> 'cancelled'
      AND s.sale_date >= (SELECT d - INTERVAL '30 days' FROM last_day)
    GROUP BY 1, 2
)
SELECT
    p.id::text                AS product_id,
    p.sku                     AS sku,
    p.name                    AS product,
    p.category                AS category,
    p.unit                    AS unit,
    p.reorder_point           AS reorder_point,
    p.lead_time_days          AS lead_time_days,
    p.cost_price::float       AS cost_price,
    b.id::text                AS branch_id,
    b.name                    AS branch,
    sup.id::text              AS supplier_id,
    sup.name                  AS supplier,
    COALESCE(st.current_stock, 0)::int         AS current_stock,
    COALESCE(d.daily_demand, 0)::float         AS daily_demand,
    COALESCE(d.units_30d, 0)::int              AS units_30d,
    (COALESCE(d.daily_demand, 0) * p.lead_time_days)::float AS lead_time_demand,
    CASE
        WHEN COALESCE(d.daily_demand, 0) > 0
        THEN (COALESCE(st.current_stock, 0)::float / d.daily_demand)
        ELSE NULL
    END::float                                 AS days_remaining
FROM products p
CROSS JOIN branches b
LEFT JOIN stock  st  ON st.branch_id  = b.id AND st.product_id = p.id
LEFT JOIN demand d   ON d.branch_id   = b.id AND d.product_id  = p.id
LEFT JOIN suppliers sup ON sup.id = p.supplier_id
WHERE 1=1
"""


# ---------------------------------------------------------------------------
# Warehouse path — reads from analytics.fact_inventory_snapshot
# ---------------------------------------------------------------------------
WAREHOUSE_SQL = """
SELECT
    p.product_id::text          AS product_id,
    p.sku                       AS sku,
    p.name                      AS product,
    p.category                  AS category,
    p.unit                      AS unit,
    p.reorder_point             AS reorder_point,
    p.lead_time_days            AS lead_time_days,
    p.cost_price::float         AS cost_price,

    l.branch_id::text           AS branch_id,
    l.branch_name               AS branch,

    s.supplier_id::text         AS supplier_id,
    s.name                      AS supplier,

    fi.current_stock            AS current_stock,
    fi.daily_demand::float      AS daily_demand,
    fi.units_last_30d           AS units_30d,
    fi.days_remaining::float    AS days_remaining,
    fi.lead_time_demand::float  AS lead_time_demand,
    fi.risk                     AS risk
FROM {fact_inventory_snapshot} fi
JOIN {dim_product}  p ON p.product_key  = fi.product_key
JOIN {dim_location} l ON l.location_key = fi.location_key
LEFT JOIN {dim_supplier} s ON s.supplier_id = p.supplier_id
WHERE 1=1
"""


def get_inventory(
    db: Session,
    branch_id: Optional[str] = None,
    risk: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    currency: str = "KES",
) -> InventoryResponse:
    params: dict = {}

    if settings.warehouse_enabled:
        sql = WAREHOUSE_SQL.format(
            fact_inventory_snapshot=_t("fact_inventory_snapshot"),
            dim_product=_t("dim_product"),
            dim_location=_t("dim_location"),
            dim_supplier=_t("dim_supplier"),
        )
    else:
        sql = OLTP_SQL

    if branch_id:
        # Both paths expose a `branch_id` column in their result rows — filter
        # via the WHERE clause against the source table.
        if settings.warehouse_enabled:
            sql += " AND l.branch_id = :branch_id"
        else:
            sql += " AND b.id = :branch_id"
        params["branch_id"] = branch_id

    if category:
        sql += " AND p.category = :category"
        params["category"] = category

    if search:
        sql += " AND (p.name ILIKE :search OR p.sku ILIKE :search)"
        params["search"] = f"%{search}%"

    if risk and settings.warehouse_enabled:
        # Warehouse has risk pre-computed — push the filter down.
        sql += " AND fi.risk = :risk"
        params["risk"] = risk.upper()

    if settings.warehouse_enabled:
        sql += " ORDER BY l.branch_name, p.name"
    else:
        sql += " ORDER BY b.name, p.name"

    rows = db.execute(text(sql), params).mappings().all()

    items: list[InventoryItem] = []

    if settings.warehouse_enabled:
        # ---------- warehouse path ------------------------------------------
        total = healthy = low = critical = 0
        value = 0.0

        for r in rows:
            status = r["risk"]
            total += 1
            value += float(r["current_stock"]) * float(r["cost_price"] or 0)
            if status == "CRITICAL":
                critical += 1
            elif status == "LOW":
                low += 1
            else:
                healthy += 1

            items.append(
                InventoryItem(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    product=r["product"],
                    category=r["category"],
                    unit=r["unit"],
                    branch_id=r["branch_id"],
                    branch=r["branch"],
                    supplier_id=r["supplier_id"],
                    supplier=r["supplier"],
                    current_stock=int(r["current_stock"]),
                    daily_demand=round(float(r["daily_demand"]), 2),
                    units_last_30d=int(r["units_30d"]),
                    days_remaining=(
                        round(float(r["days_remaining"]), 1)
                        if r["days_remaining"] is not None
                        else None
                    ),
                    lead_time_days=int(r["lead_time_days"]),
                    lead_time_demand=round(float(r["lead_time_demand"]), 1),
                    reorder_point=int(r["reorder_point"]),
                    risk=status,
                )
            )

    else:
        # ---------- OLTP path ------------------------------------------------
        if risk:
            # risk filter is applied in Python on this path because the SQL
            # doesn't know the classification.
            pass

        total = healthy = low = critical = 0
        value = 0.0
        for r in rows:
            status = _classify(
                current_stock=int(r["current_stock"]),
                daily_demand=float(r["daily_demand"]),
                lead_time_days=int(r["lead_time_days"]),
                lead_time_demand=float(r["lead_time_demand"]),
                reorder_point=int(r["reorder_point"]),
            )

            total += 1
            value += float(r["current_stock"]) * float(r["cost_price"] or 0)

            if status == "CRITICAL":
                critical += 1
            elif status == "LOW":
                low += 1
            else:
                healthy += 1

            if risk and risk.upper() != status:
                continue

            items.append(
                InventoryItem(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    product=r["product"],
                    category=r["category"],
                    unit=r["unit"],
                    branch_id=r["branch_id"],
                    branch=r["branch"],
                    supplier_id=r["supplier_id"],
                    supplier=r["supplier"],
                    current_stock=int(r["current_stock"]),
                    daily_demand=round(float(r["daily_demand"]), 2),
                    units_last_30d=int(r["units_30d"]),
                    days_remaining=(
                        round(float(r["days_remaining"]), 1)
                        if r["days_remaining"] is not None
                        else None
                    ),
                    lead_time_days=int(r["lead_time_days"]),
                    lead_time_demand=round(float(r["lead_time_demand"]), 1),
                    reorder_point=int(r["reorder_point"]),
                    risk=status,
                )
            )

    # Sort: most critical first, then by days remaining
    order = {"CRITICAL": 0, "LOW": 1, "HEALTHY": 2}
    items.sort(
        key=lambda i: (
            order[i.risk],
            i.days_remaining if i.days_remaining is not None else 9999,
        )
    )

    summary = InventorySummary(
        total_skus=total,
        healthy=healthy,
        low=low,
        critical=critical,
        total_inventory_value=round(value, 2),
        currency=currency,
    )

    return InventoryResponse(summary=summary, items=items)