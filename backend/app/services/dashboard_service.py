from datetime import date, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.dashboard import (
    CashflowPoint,
    DashboardKpis,
    DashboardResponse,
    InventoryRiskItem,
    RecommendationSummary,
    RevenuePoint,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


def _latest_sale_date(db: Session) -> date:
    return (
        db.execute(text(f"SELECT MAX(sale_date)::date FROM {_t('sales')}")).scalar()
        or date.today()
    )


def get_dashboard(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    branch_id: Optional[str] = None,
    currency: str = "KES",
) -> DashboardResponse:
    if date_to is None:
        date_to = _latest_sale_date(db)
    if date_from is None:
        date_from = date_to - timedelta(days=30)

    params: dict = {
        "since": date_from,
        "until_excl": date_to + timedelta(days=1),
    }
    branch_clause = ""
    if branch_id:
        branch_clause = " AND s.branch_id = :branch_id"
        params["branch_id"] = branch_id

    # ---- KPIs -----------------------------------------------------------
    if settings.warehouse_enabled:
        branch_wh = ""
        if branch_id:
            branch_wh = (
                f" AND f.location_key = (SELECT location_key FROM {_t('dim_location')} "
                f"WHERE branch_id = :branch_id)"
            )
        kpi_row = db.execute(
            text(
                f"""
                SELECT
                    COALESCE(SUM(f.revenue), 0)::float       AS revenue,
                    COALESCE(SUM(f.gross_profit), 0)::float  AS gross_profit
                FROM {_t('fact_sales')} f
                WHERE f.status <> 'cancelled'
                  AND f.sale_date >= :since
                  AND f.sale_date <  :until_excl
                  {branch_wh}
                """
            ),
            params,
        ).mappings().one()
    else:
        kpi_row = db.execute(
            text(
                f"""
                SELECT
                    COALESCE(SUM(si.quantity * si.unit_price), 0)::float AS revenue,
                    COALESCE(SUM(si.quantity * (si.unit_price - si.unit_cost)), 0)::float
                        AS gross_profit
                FROM sale_items si
                JOIN sales s ON s.id = si.sale_id
                WHERE s.status <> 'cancelled'
                  AND s.sale_date >= :since
                  AND s.sale_date <  :until_excl
                  {branch_clause}
                """
            ),
            params,
        ).mappings().one()

    revenue = float(kpi_row["revenue"] or 0.0)
    gross_profit = float(kpi_row["gross_profit"] or 0.0)

    # ---- Inventory value ------------------------------------------------
    if settings.warehouse_enabled:
        inv_params: dict = {}
        inv_branch = ""
        if branch_id:
            inv_branch = (
                f" AND fi.location_key = (SELECT location_key FROM {_t('dim_location')} "
                f"WHERE branch_id = :branch_id)"
            )
            inv_params["branch_id"] = branch_id
        inventory_value = float(
            db.execute(
                text(
                    f"""
                    SELECT COALESCE(SUM(fi.inventory_value), 0)::float
                    FROM {_t('fact_inventory_snapshot')} fi
                    WHERE 1=1 {inv_branch}
                    """
                ),
                inv_params,
            ).scalar()
            or 0.0
        )
    else:
        inv_params: dict = {}
        inv_branch = ""
        if branch_id:
            inv_branch = " AND branch_id = :branch_id"
            inv_params["branch_id"] = branch_id
        inventory_value = float(
            db.execute(
                text(
                    f"""
                    WITH net AS (
                        SELECT branch_id, product_id,
                               SUM(CASE WHEN movement_type = 'in'  THEN quantity
                                        WHEN movement_type = 'out' THEN -quantity
                                        ELSE quantity END) AS qty
                        FROM inventory_movements
                        WHERE 1=1 {inv_branch}
                        GROUP BY 1, 2
                    )
                    SELECT COALESCE(SUM(GREATEST(n.qty, 0) * p.cost_price), 0)::float
                    FROM net n
                    JOIN products p ON p.id = n.product_id
                    """
                ),
                inv_params,
            ).scalar()
            or 0.0
        )

    # ---- Outstanding payments -------------------------------------------
    if settings.warehouse_enabled:
        out_branch = ""
        out_params: dict = {}
        if branch_id:
            out_branch = (
                f" AND location_key = (SELECT location_key FROM {_t('dim_location')} "
                f"WHERE branch_id = :branch_id)"
            )
            out_params["branch_id"] = branch_id
        outstanding_payments = float(
            db.execute(
                text(
                    f"""
                    SELECT COALESCE(SUM(revenue), 0)::float
                    FROM {_t('fact_sales')}
                    WHERE status = 'pending' {out_branch}
                    """
                ),
                out_params,
            ).scalar()
            or 0.0
        )
    else:
        out_branch = ""
        out_params: dict = {}
        if branch_id:
            out_branch = " AND branch_id = :branch_id"
            out_params["branch_id"] = branch_id
        outstanding_payments = float(
            db.execute(
                text(
                    f"""
                    SELECT COALESCE(SUM(total_amount), 0)::float
                    FROM sales
                    WHERE status = 'pending' {out_branch}
                    """
                ),
                out_params,
            ).scalar()
            or 0.0
        )

    # ---- Cash balance (always from OLTP) --------------------------------
    cash_params: dict = {}
    cash_branch = ""
    if branch_id:
        cash_branch = " AND branch_id = :branch_id"
        cash_params["branch_id"] = branch_id

    cash_balance = float(
        db.execute(
            text(
                f"""
                SELECT COALESCE(SUM(balance), 0)::float
                FROM cash_accounts
                WHERE 1=1 {cash_branch}
                """
            ),
            cash_params,
        ).scalar()
        or 0.0
    )

    # ---- Revenue trend --------------------------------------------------
    if settings.warehouse_enabled:
        branch_wh = ""
        if branch_id:
            branch_wh = (
                f" AND f.location_key = (SELECT location_key FROM {_t('dim_location')} "
                f"WHERE branch_id = :branch_id)"
            )
        trend_rows = db.execute(
            text(
                f"""
                SELECT f.sale_date::date AS day,
                       SUM(f.revenue)::float AS value
                FROM {_t('fact_sales')} f
                WHERE f.status <> 'cancelled'
                  AND f.sale_date >= :since
                  AND f.sale_date <  :until_excl
                  {branch_wh}
                GROUP BY 1 ORDER BY 1
                """
            ),
            params,
        ).mappings().all()
    else:
        trend_rows = db.execute(
            text(
                f"""
                SELECT s.sale_date::date AS day,
                       SUM(si.quantity * si.unit_price)::float AS value
                FROM sale_items si
                JOIN sales s ON s.id = si.sale_id
                WHERE s.status <> 'cancelled'
                  AND s.sale_date >= :since
                  AND s.sale_date <  :until_excl
                  {branch_clause}
                GROUP BY 1 ORDER BY 1
                """
            ),
            params,
        ).mappings().all()

    revenue_trend = [
        RevenuePoint(date=r["day"], value=round(float(r["value"] or 0.0), 2))
        for r in trend_rows
    ]

    # ---- Cash-flow projection (trailing mean random walk) ---------------
    flow_rows = db.execute(
        text(
            f"""
            SELECT payment_date::date AS day,
                   SUM(CASE WHEN direction = 'in' THEN amount ELSE -amount END)::float
                       AS net
            FROM {_t('payments')}
            WHERE payment_date >= :since
            GROUP BY 1 ORDER BY 1
            """
        ),
        {"since": date_to - timedelta(days=30)},
    ).mappings().all()

    nets = [float(r["net"] or 0.0) for r in flow_rows]
    if nets:
        mean_net = sum(nets) / len(nets)
        var = sum((n - mean_net) ** 2 for n in nets) / max(len(nets) - 1, 1)
        std_net = var ** 0.5
    else:
        mean_net = 0.0
        std_net = 0.0

    band_per_day = 1.28 * std_net
    cashflow_forecast: list[CashflowPoint] = []
    for i in range(1, 31):
        projected = date_to + timedelta(days=i)
        center = cash_balance + mean_net * i
        band = band_per_day * (i ** 0.5)
        cashflow_forecast.append(
            CashflowPoint(
                date=projected,
                balance=round(center, 2),
                lower=round(center - band, 2),
                upper=round(center + band, 2),
            )
        )

    # ---- Inventory risk -------------------------------------------------
    if settings.warehouse_enabled:
        risk_rows = db.execute(
            text(
                f"""
                SELECT
                    l.branch_id::text  AS branch_id,
                    l.branch_name      AS branch,
                    p.product_id::text AS product_id,
                    p.name             AS product,
                    fi.current_stock   AS current_stock,
                    fi.daily_demand::float AS daily_demand,
                    fi.days_remaining::float AS days_remaining,
                    fi.reorder_point   AS reorder_point,
                    fi.lead_time_days  AS lead_time_days,
                    fi.risk            AS wh_risk
                FROM {_t('fact_inventory_snapshot')} fi
                JOIN {_t('dim_product')}  p ON p.product_key  = fi.product_key
                JOIN {_t('dim_location')} l ON l.location_key = fi.location_key
                WHERE fi.risk <> 'HEALTHY'
                ORDER BY CASE fi.risk WHEN 'CRITICAL' THEN 0 ELSE 1 END,
                         fi.days_remaining ASC
                LIMIT 20
                """
            ),
            {},
        ).mappings().all()
    else:
        risk_rows = db.execute(
            text(
                """
                WITH net AS (
                    SELECT branch_id, product_id,
                           SUM(CASE WHEN movement_type = 'in'  THEN quantity
                                    WHEN movement_type = 'out' THEN -quantity
                                    ELSE quantity END) AS stock
                    FROM inventory_movements
                    GROUP BY 1, 2
                ),
                demand AS (
                    SELECT s.branch_id     AS branch_id,
                           si.product_id   AS product_id,
                           SUM(si.quantity)::float / 30.0 AS daily_demand
                    FROM sale_items si
                    JOIN sales s ON s.id = si.sale_id
                    WHERE s.status <> 'cancelled'
                      AND s.sale_date >= (
                            SELECT MAX(sale_date)::date - INTERVAL '30 days' FROM sales
                      )
                    GROUP BY 1, 2
                )
                SELECT
                    b.id::text  AS branch_id,
                    b.name      AS branch,
                    p.id::text  AS product_id,
                    p.name      AS product,
                    GREATEST(n.stock, 0)::int AS current_stock,
                    COALESCE(d.daily_demand, 0)::float AS daily_demand,
                    p.reorder_point,
                    p.lead_time_days,
                    CASE
                        WHEN COALESCE(d.daily_demand, 0) > 0
                            THEN GREATEST(n.stock, 0)::float / d.daily_demand
                        ELSE 9999
                    END AS days_remaining
                FROM net n
                JOIN products p ON p.id = n.product_id
                JOIN branches b ON b.id = n.branch_id
                LEFT JOIN demand d
                    ON d.branch_id  = n.branch_id
                   AND d.product_id = n.product_id
                WHERE GREATEST(n.stock, 0) < p.reorder_point * 3
                ORDER BY days_remaining ASC
                LIMIT 20
                """
            ),
            {},
        ).mappings().all()

    inventory_risk: list[InventoryRiskItem] = []
    for r in risk_rows:
        dr = float(r["days_remaining"])
        lead = int(r["lead_time_days"] or 3)

        if settings.warehouse_enabled:
            wh = r["wh_risk"]
            risk = "HIGH" if wh == "CRITICAL" else "MEDIUM" if wh == "LOW" else "LOW"
        else:
            if dr <= lead:
                risk = "HIGH"
            elif dr <= lead * 2:
                risk = "MEDIUM"
            else:
                risk = "LOW"

        inventory_risk.append(
            InventoryRiskItem(
                product_id=r["product_id"],
                product=r["product"],
                branch_id=r["branch_id"],
                branch=r["branch"],
                current_stock=int(r["current_stock"]),
                daily_demand=round(float(r["daily_demand"]), 2),
                days_remaining=round(dr, 1),
                reorder_point=int(r["reorder_point"]),
                risk=risk,
            )
        )

    # ---- Recommendations (stub — full engine in recommendation_service) --
    recommendations: list[RecommendationSummary] = []

    for item in inventory_risk:
        if item.risk == "HIGH":
            recommendations.append(
                RecommendationSummary(
                    id=f"inv-{item.product_id}-{item.branch_id}",
                    type="inventory",
                    title=(
                        f"Restock {item.product} at {item.branch} — "
                        f"{item.days_remaining} days left"
                    ),
                    priority="high",
                )
            )

    min_safe = float(
        db.execute(
            text("SELECT COALESCE(MIN(min_safe_balance), 150000)::float FROM cash_accounts")
        ).scalar()
        or 150000.0
    )
    for point in cashflow_forecast:
        if point.balance < min_safe:
            recommendations.append(
                RecommendationSummary(
                    id="cash-shortage",
                    type="cashflow",
                    title=(
                        f"Cash may fall below {min_safe:,.0f} "
                        f"on {point.date.isoformat()}"
                    ),
                    priority="high",
                )
            )
            break

    return DashboardResponse(
        kpis=DashboardKpis(
            revenue=round(revenue, 2),
            gross_profit=round(gross_profit, 2),
            inventory_value=round(inventory_value, 2),
            outstanding_payments=round(outstanding_payments, 2),
            cash_balance=round(cash_balance, 2),
            currency=currency,
        ),
        revenue_trend=revenue_trend,
        cashflow_forecast=cashflow_forecast,
        inventory_risk=inventory_risk,
        recommendations=recommendations[:6],
    )