from datetime import date, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.sales import (
    CategoryRevenue,
    LocationRevenue,
    ProductRevenue,
    SalesKpis,
    SalesResponse,
    TimePoint,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


# ---------------------------------------------------------------------------
# Date + filter helpers
# ---------------------------------------------------------------------------
def _resolve_dates(
    db: Session,
    date_from: Optional[date],
    date_to: Optional[date],
) -> tuple[date, date]:
    if date_to is None:
        date_to = (
            db.execute(text(f"SELECT MAX(sale_date)::date FROM {_t('sales')}")).scalar()
            or date.today()
        )
    if date_from is None:
        date_from = date_to - timedelta(days=90)
    return date_from, date_to


def _build_filter_cte(
    date_from: date,
    date_to: date,
    branch_id: Optional[str],
    product_id: Optional[str],
    customer_id: Optional[str],
) -> tuple[str, dict]:
    """
    Return (cte_sql, params). The CTE is always named `filtered_items` and
    always exposes: item_id, sale_id, product_id, quantity, unit_price,
    unit_cost, sale_date, branch_id, customer_id — regardless of source.
    """
    params: dict = {
        "date_from": date_from,
        "date_to_excl": date_to + timedelta(days=1),
    }

    if not settings.warehouse_enabled:
        # ---------- OLTP path ---------------------------------------------
        clauses = [
            "s.status <> 'cancelled'",
            "s.sale_date >= :date_from",
            "s.sale_date <  :date_to_excl",
        ]
        if branch_id:
            clauses.append("s.branch_id = :branch_id")
            params["branch_id"] = branch_id
        if customer_id:
            clauses.append("s.customer_id = :customer_id")
            params["customer_id"] = customer_id
        if product_id:
            clauses.append("si.product_id = :product_id")
            params["product_id"] = product_id

        cte = f"""
        WITH filtered_items AS (
            SELECT
                si.id           AS item_id,
                si.sale_id      AS sale_id,
                si.product_id   AS product_id,
                si.quantity     AS quantity,
                si.unit_price   AS unit_price,
                si.unit_cost    AS unit_cost,
                s.sale_date     AS sale_date,
                s.branch_id     AS branch_id,
                s.customer_id   AS customer_id
            FROM public.sale_items si
            JOIN public.sales s ON s.id = si.sale_id
            WHERE {' AND '.join(clauses)}
        )
        """
        return cte, params

    # ---------- Warehouse path -------------------------------------------
    clauses = [
        "f.status <> 'cancelled'",
        "f.sale_date >= :date_from",
        "f.sale_date <  :date_to_excl",
    ]
    if branch_id:
        clauses.append(
            f"f.location_key = (SELECT location_key FROM {_t('dim_location')} "
            f"WHERE branch_id = :branch_id)"
        )
        params["branch_id"] = branch_id
    if customer_id:
        clauses.append(
            f"f.customer_key = (SELECT customer_key FROM {_t('dim_customer')} "
            f"WHERE customer_id = :customer_id)"
        )
        params["customer_id"] = customer_id
    if product_id:
        clauses.append(
            f"f.product_key = (SELECT product_key FROM {_t('dim_product')} "
            f"WHERE product_id = :product_id)"
        )
        params["product_id"] = product_id

    cte = f"""
    WITH filtered_items AS (
        SELECT
            f.sale_key      AS item_id,
            f.sale_id       AS sale_id,
            p.product_id    AS product_id,
            f.quantity      AS quantity,
            f.unit_price    AS unit_price,
            f.unit_cost     AS unit_cost,
            f.sale_date     AS sale_date,
            l.branch_id     AS branch_id,
            c.customer_id   AS customer_id
        FROM {_t('fact_sales')} f
        LEFT JOIN {_t('dim_product')}  p ON p.product_key  = f.product_key
        LEFT JOIN {_t('dim_location')} l ON l.location_key = f.location_key
        LEFT JOIN {_t('dim_customer')} c ON c.customer_key = f.customer_key
        WHERE {' AND '.join(clauses)}
    )
    """
    return cte, params


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_sales_analytics(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    branch_id: Optional[str] = None,
    product_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    currency: str = "KES",
) -> SalesResponse:
    date_from, date_to = _resolve_dates(db, date_from, date_to)
    cte, params = _build_filter_cte(
        date_from, date_to, branch_id, product_id, customer_id
    )

    # ---- KPIs -----------------------------------------------------------
    kpi_row = db.execute(
        text(
            cte
            + """
            SELECT
                COALESCE(SUM(quantity * unit_price), 0)::float AS revenue,
                COUNT(DISTINCT sale_id)::int                   AS orders,
                COALESCE(SUM(quantity * unit_cost), 0)::float  AS cost
            FROM filtered_items
            """
        ),
        params,
    ).mappings().one()

    revenue = float(kpi_row["revenue"] or 0.0)
    orders = int(kpi_row["orders"] or 0)
    cost = float(kpi_row["cost"] or 0.0)
    aov = round(revenue / orders, 2) if orders else 0.0
    gross_margin = round((revenue - cost) / revenue, 4) if revenue else 0.0

    # ---- Revenue over time ----------------------------------------------
    time_rows = db.execute(
        text(
            cte
            + """
            SELECT sale_date::date AS day,
                   SUM(quantity * unit_price)::float AS value
            FROM filtered_items
            GROUP BY 1 ORDER BY 1
            """
        ),
        params,
    ).mappings().all()

    revenue_over_time = [
        TimePoint(date=r["day"], value=round(float(r["value"] or 0.0), 2))
        for r in time_rows
    ]

    # ---- Product dimension lookup ---------------------------------------
    if settings.warehouse_enabled:
        product_join = (
            f"JOIN {_t('dim_product')} p ON p.product_id = fi.product_id"
        )
        product_id_col = "p.product_id::text"
        product_name_col = "p.name"
        product_cat_col = "p.category"
    else:
        product_join = "JOIN public.products p ON p.id = fi.product_id"
        product_id_col = "p.id::text"
        product_name_col = "p.name"
        product_cat_col = "p.category"

    # ---- Revenue by product ---------------------------------------------
    product_rows = db.execute(
        text(
            cte
            + f"""
            SELECT {product_id_col} AS product_id,
                   {product_name_col} AS product,
                   {product_cat_col} AS category,
                   SUM(fi.quantity * fi.unit_price)::float AS revenue,
                   SUM(fi.quantity)::int                   AS units
            FROM filtered_items fi
            {product_join}
            GROUP BY 1, 2, 3
            ORDER BY revenue DESC
            """
        ),
        params,
    ).mappings().all()

    revenue_by_product = [
        ProductRevenue(
            product_id=r["product_id"],
            product=r["product"],
            category=r["category"],
            revenue=round(float(r["revenue"] or 0.0), 2),
            units=int(r["units"] or 0),
        )
        for r in product_rows
    ]

    # ---- Revenue by category --------------------------------------------
    category_rows = db.execute(
        text(
            cte
            + f"""
            SELECT COALESCE({product_cat_col}, 'Uncategorized') AS category,
                   SUM(fi.quantity * fi.unit_price)::float AS revenue
            FROM filtered_items fi
            {product_join}
            GROUP BY 1
            ORDER BY revenue DESC
            """
        ),
        params,
    ).mappings().all()

    revenue_by_category = [
        CategoryRevenue(category=r["category"], revenue=round(float(r["revenue"] or 0.0), 2))
        for r in category_rows
    ]

    # ---- Revenue by location --------------------------------------------
    if settings.warehouse_enabled:
        location_join = (
            f"JOIN {_t('dim_location')} l ON l.branch_id = fi.branch_id"
        )
        location_id_col = "l.branch_id::text"
        location_name_col = "l.branch_name"
    else:
        location_join = "JOIN public.branches b ON b.id = fi.branch_id"
        location_id_col = "b.id::text"
        location_name_col = "b.name"

    location_rows = db.execute(
        text(
            cte
            + f"""
            SELECT {location_id_col} AS location_id,
                   {location_name_col} AS location,
                   SUM(fi.quantity * fi.unit_price)::float AS revenue
            FROM filtered_items fi
            {location_join}
            GROUP BY 1, 2
            ORDER BY revenue DESC
            """
        ),
        params,
    ).mappings().all()

    revenue_by_location = [
        LocationRevenue(
            location_id=r["location_id"],
            location=r["location"],
            revenue=round(float(r["revenue"] or 0.0), 2),
        )
        for r in location_rows
    ]

    top_products = revenue_by_product[:10]
    bottom_products = [p for p in reversed(revenue_by_product) if p.units > 0][:10]

    return SalesResponse(
        kpis=SalesKpis(
            revenue=round(revenue, 2),
            orders=orders,
            avg_order_value=aov,
            gross_margin=gross_margin,
            currency=currency,
        ),
        revenue_over_time=revenue_over_time,
        revenue_by_product=revenue_by_product,
        revenue_by_category=revenue_by_category,
        revenue_by_location=revenue_by_location,
        top_products=top_products,
        bottom_products=bottom_products,
    )