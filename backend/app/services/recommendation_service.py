"""
Compose the five domain services into a single ranked recommendations feed.

Each card carries a real number from the data — no generic advice.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.recommendations import (
    Recommendation,
    RecommendationsResponse,
    RecommendationTotals,
)
from app.services import (
    cashflow_service,
    customer_service,
    inventory_service,
    supplier_service,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


# ---------------------------------------------------------------------------
# Priority banding — score is a composite of financial exposure + urgency
# ---------------------------------------------------------------------------
def _band(score: float) -> str:
    if score >= 500_000:      # ≥ 500k KES or equivalent urgency
        return "high"
    if score >= 100_000:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------
def _inventory_recommendations(inventory) -> list[Recommendation]:
    cards: list[Recommendation] = []

    critical = [i for i in inventory.items if i.risk == "CRITICAL"]

    for item in critical[:3]:
        # Reorder target = 2.5 × lead-time demand, floored at reorder point
        target = max(
            item.reorder_point,
            math.ceil(item.daily_demand * item.lead_time_days * 2.5),
        )
        reorder_qty = max(0, target - item.current_stock)

        if reorder_qty <= 0:
            continue

        days = item.days_remaining or 0.0
        lead = item.lead_time_days

        # Stockout probability heuristic: ~100% if days < lead, decaying after
        stockout_prob = min(0.95, max(0.05, 1.0 - days / max(lead * 3, 1)))

        # Priority score: high when days are much smaller than lead time
        urgency = max(0.0, lead - days) + 1.0
        score = item.daily_demand * urgency * 100_000

        cards.append(
            Recommendation(
                id=f"inv-{item.product_id}-{item.branch_id}",
                type="inventory",
                priority=_band(score),
                priority_score=score,
                title=f"Restock {item.product} at {item.branch}",
                problem=(
                    f"{item.product} at {item.branch} is projected to stock out "
                    f"in {days:.1f} days."
                ),
                evidence=(
                    f"Current stock: {item.current_stock} {item.unit or 'units'}. "
                    f"Daily demand: {item.daily_demand:.1f}/day. "
                    f"Lead time: {lead} days (lead-time demand "
                    f"{item.lead_time_demand:.0f}). Reorder point: "
                    f"{item.reorder_point}. Days remaining: {days:.1f}."
                ),
                recommendation=(
                    f"Place a purchase order for {reorder_qty} units of "
                    f"{item.product} from {item.supplier or 'the primary supplier'}."
                ),
                expected_impact=(
                    f"Restores roughly "
                    f"{(item.current_stock + reorder_qty) / max(item.daily_demand, 0.01):.0f} "
                    f"days of coverage and reduces stockout probability from "
                    f"{stockout_prob * 100:.0f}% to under 15%."
                ),
            )
        )

    # A softer "LOW" alert for a couple of items below reorder point
    low_items = [i for i in inventory.items if i.risk == "LOW"][:2]
    for item in low_items:
        reorder_qty = max(
            item.reorder_point,
            math.ceil(item.daily_demand * item.lead_time_days * 2.5),
        ) - item.current_stock

        if reorder_qty <= 0:
            continue

        score = item.daily_demand * item.lead_time_days * 25_000

        cards.append(
            Recommendation(
                id=f"invlow-{item.product_id}-{item.branch_id}",
                type="inventory",
                priority="low",
                priority_score=score,
                title=f"Reorder {item.product} soon",
                problem=(
                    f"{item.product} at {item.branch} is at {item.current_stock} "
                    f"units, below the reorder point of {item.reorder_point}."
                ),
                evidence=(
                    f"Daily demand: {item.daily_demand:.1f}/day. Days remaining: "
                    f"{item.days_remaining or 0:.1f}. Lead time: "
                    f"{item.lead_time_days} days."
                ),
                recommendation=(
                    f"Schedule an order of {reorder_qty} units within the next "
                    f"{(item.days_remaining or 0):.0f} days."
                ),
                expected_impact=(
                    "Prevents the SKU from slipping into CRITICAL status next "
                    "week and keeps service levels above 95%."
                ),
            )
        )

    return cards


# ---------------------------------------------------------------------------
# Cash-flow
# ---------------------------------------------------------------------------
def _cashflow_recommendations(cashflow) -> list[Recommendation]:
    if not cashflow.alert:
        return []

    alert = cashflow.alert
    shortfall = max(0.0, alert.minimum_safe_balance - alert.expected_minimum)

    # Priority proportional to shortfall
    score = shortfall * 2.0

    return [
        Recommendation(
            id="cash-shortage",
            type="cashflow",
            priority=_band(score),
            priority_score=score,
            title=f"Cash shortage projected on {alert.predicted_date}",
            problem=(
                f"Cash balance is projected to fall below the minimum safe "
                f"threshold of {alert.minimum_safe_balance:,.0f} on "
                f"{alert.predicted_date}, bottoming at "
                f"{alert.expected_minimum:,.0f}."
            ),
            evidence=(
                f"Current cash: {cashflow.summary.current_cash:,.0f}. "
                f"Expected 30-day income: {cashflow.summary.expected_income:,.0f}. "
                f"Expected 30-day expenses: "
                f"{cashflow.summary.expected_expenses:,.0f}. "
                f"Projected shortfall: {shortfall:,.0f}."
            ),
            recommendation=alert.recommendation,
            expected_impact=(
                f"Recovering {shortfall:,.0f} keeps the balance above the "
                f"minimum threshold through the full 30-day horizon."
            ),
        )
    ]


# ---------------------------------------------------------------------------
# Pricing — products trading below their category median margin
# ---------------------------------------------------------------------------
PRICING_SQL_OLTP = """
WITH last_day AS (SELECT MAX(sale_date)::date AS d FROM sales),
sales_90 AS (
    SELECT si.product_id AS product_id,
           SUM(si.quantity)::int                     AS units,
           SUM(si.quantity * si.unit_price)::float   AS revenue,
           SUM(si.quantity * si.unit_cost)::float    AS cost
    FROM sale_items si
    JOIN sales s ON s.id = si.sale_id
    WHERE s.status <> 'cancelled'
      AND s.sale_date >= (SELECT d - INTERVAL '90 days' FROM last_day)
    GROUP BY 1
),
with_margin AS (
    SELECT p.id::text AS product_id, p.name AS product, p.category,
           p.sell_price::float AS current_price,
           s90.units, s90.revenue, s90.cost,
           CASE WHEN s90.revenue > 0
                THEN (s90.revenue - s90.cost) / s90.revenue
                ELSE 0 END AS margin
    FROM products p
    JOIN sales_90 s90 ON s90.product_id = p.id
),
category_median AS (
    SELECT category,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY margin) AS med_margin
    FROM with_margin
    GROUP BY category
)
SELECT wm.product_id, wm.product, wm.category,
       wm.current_price, wm.units, wm.revenue, wm.cost, wm.margin,
       cm.med_margin
FROM with_margin wm
JOIN category_median cm ON cm.category = wm.category
WHERE wm.margin < cm.med_margin - 0.03
  AND wm.units >= 15
ORDER BY (cm.med_margin - wm.margin) * wm.revenue DESC
LIMIT 2
"""


PRICING_SQL_WAREHOUSE = """
WITH last_day AS (
    SELECT MAX(sale_date)::date AS d FROM {fact_sales}
),
sales_90 AS (
    SELECT p.product_id                          AS product_id,
           SUM(f.quantity)::int                  AS units,
           SUM(f.revenue)::float                 AS revenue,
           SUM(f.quantity * f.unit_cost)::float  AS cost
    FROM {fact_sales} f
    JOIN {dim_product} p ON p.product_key = f.product_key
    WHERE f.status <> 'cancelled'
      AND f.sale_date >= (SELECT d - INTERVAL '90 days' FROM last_day)
    GROUP BY 1
),
with_margin AS (
    SELECT p.product_id::text AS product_id, p.name AS product, p.category,
           p.sell_price::float AS current_price,
           s90.units, s90.revenue, s90.cost,
           CASE WHEN s90.revenue > 0
                THEN (s90.revenue - s90.cost) / s90.revenue
                ELSE 0 END AS margin
    FROM {dim_product} p
    JOIN sales_90 s90 ON s90.product_id = p.product_id
),
category_median AS (
    SELECT category,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY margin) AS med_margin
    FROM with_margin
    GROUP BY category
)
SELECT wm.product_id, wm.product, wm.category,
       wm.current_price, wm.units, wm.revenue, wm.cost, wm.margin,
       cm.med_margin
FROM with_margin wm
JOIN category_median cm ON cm.category = wm.category
WHERE wm.margin < cm.med_margin - 0.03
  AND wm.units >= 15
ORDER BY (cm.med_margin - wm.margin) * wm.revenue DESC
LIMIT 2
"""


def _pricing_recommendations(db: Session) -> list[Recommendation]:
    if settings.warehouse_enabled:
        sql = PRICING_SQL_WAREHOUSE.format(
            fact_sales=_t("fact_sales"),
            dim_product=_t("dim_product"),
        )
    else:
        sql = PRICING_SQL_OLTP

    rows = db.execute(text(sql)).mappings().all()
    cards: list[Recommendation] = []

    for r in rows:
        units = int(r["units"] or 0)
        revenue = float(r["revenue"] or 0.0)
        cost = float(r["cost"] or 0.0)
        margin = float(r["margin"] or 0.0)
        med = float(r["med_margin"] or 0.0)
        gap_pp = (med - margin) * 100.0
        current_price = float(r["current_price"] or 0.0)

        if units <= 0 or med >= 0.99:
            continue

        # Price to hit the category median margin
        cost_per_unit = cost / units
        target_price = cost_per_unit / (1.0 - med) if med < 0.99 else current_price
        price_increase = max(0.0, target_price - current_price)
        delta_revenue = price_increase * units  # over 90 days at current volume

        score = delta_revenue
        cards.append(
            Recommendation(
                id=f"price-{r['product_id']}",
                type="pricing",
                priority=_band(score),
                priority_score=score,
                title=f"Raise price on {r['product']}",
                problem=(
                    f"{r['product']}'s gross margin ({margin * 100:.1f}%) is "
                    f"{gap_pp:.1f} pp below the {r['category']} median "
                    f"({med * 100:.1f}%)."
                ),
                evidence=(
                    f"Units sold (last 90 days): {units}. Revenue: "
                    f"{revenue:,.0f}. Current price: {current_price:,.0f}. "
                    f"Cost per unit: {cost_per_unit:,.0f}."
                ),
                recommendation=(
                    f"Raise the sell price from {current_price:,.0f} to "
                    f"{target_price:,.0f} to bring the margin in line with the "
                    f"{r['category']} median."
                ),
                expected_impact=(
                    f"Adds roughly {delta_revenue:,.0f} in gross revenue over "
                    f"90 days at current volume."
                ),
            )
        )

    return cards


# ---------------------------------------------------------------------------
# Customer — At Risk win-back and High Value retention
# ---------------------------------------------------------------------------
def _customer_recommendations(customers) -> list[Recommendation]:
    by_segment = {s.segment: s for s in customers.segments}
    cards: list[Recommendation] = []

    # At Risk win-back
    at_risk = by_segment.get("At Risk")
    if at_risk and at_risk.count >= 10:
        est_lift = at_risk.revenue * 0.20  # 20% win-back assumption
        score = est_lift

        cards.append(
            Recommendation(
                id="cust-at-risk",
                type="customer",
                priority=_band(score),
                priority_score=score,
                title=f"Win back {at_risk.count} at-risk customers",
                problem=(
                    f"{at_risk.count} customers who historically generated "
                    f"{at_risk.revenue:,.0f} in revenue haven't purchased "
                    f"recently."
                ),
                evidence=(
                    f"Avg days since last purchase: {at_risk.avg_recency_days:.0f}. "
                    f"Avg orders per customer: {at_risk.avg_frequency:.1f}. "
                    f"Avg lifetime spend: {at_risk.avg_monetary:,.0f}. "
                    f"Revenue share: {at_risk.revenue_share * 100:.1f}%."
                ),
                recommendation=(
                    "Launch a targeted win-back campaign on WhatsApp/SMS with a "
                    "5–10% incentive on the products each customer previously "
                    "bought most."
                ),
                expected_impact=(
                    f"Re-engaging 20% of this segment adds approximately "
                    f"{est_lift:,.0f} in repeat revenue."
                ),
            )
        )

    # High Value retention
    high_value = by_segment.get("High Value")
    if high_value and high_value.count >= 5:
        est_protected = high_value.revenue * 0.10
        score = est_protected

        cards.append(
            Recommendation(
                id="cust-high-value",
                type="customer",
                priority=_band(score),
                priority_score=score,
                title=f"Protect {high_value.count} high-value customers",
                problem=(
                    f"{high_value.count} customers account for "
                    f"{high_value.revenue_share * 100:.0f}% of revenue — losing "
                    f"even a handful materially impacts cash flow."
                ),
                evidence=(
                    f"Combined lifetime revenue: {high_value.revenue:,.0f}. "
                    f"Avg spend per customer: {high_value.avg_monetary:,.0f}. "
                    f"Avg orders: {high_value.avg_frequency:.1f}. Avg recency: "
                    f"{high_value.avg_recency_days:.0f} days."
                ),
                recommendation=(
                    "Assign these accounts to a named relationship owner and "
                    "schedule a proactive check-in call or WhatsApp within the "
                    "next 14 days."
                ),
                expected_impact=(
                    f"Preventing a 10% churn in this segment preserves "
                    f"approximately {est_protected:,.0f} in annualized revenue."
                ),
            )
        )

    return cards


# ---------------------------------------------------------------------------
# Supplier — degrading suppliers
# ---------------------------------------------------------------------------
def _supplier_recommendations(suppliers) -> list[Recommendation]:
    cards: list[Recommendation] = []
    degrading = [s for s in suppliers.suppliers if s.trend == "degrading"]

    for sup in degrading[:2]:
        drop_pp = (sup.on_time_pct - sup.recent_on_time_pct) * 100.0
        # Assume 30% of their volume is shiftable in the next quarter
        shiftable_orders = math.floor(sup.orders * 0.30)

        # Priority score: how much reliability gap × order volume
        score = max(0.0, drop_pp) * max(1, sup.orders) * 1_000

        cards.append(
            Recommendation(
                id=f"sup-{sup.supplier_id}",
                type="supplier",
                priority=_band(score),
                priority_score=score,
                title=f"Review contract with {sup.supplier}",
                problem=(
                    f"{sup.supplier}'s on-time delivery has dropped from "
                    f"{sup.on_time_pct * 100:.0f}% overall to "
                    f"{sup.recent_on_time_pct * 100:.0f}% in the last 90 days "
                    f"({drop_pp:.0f} pp decline)."
                ),
                evidence=(
                    f"{sup.orders} purchase orders on record. Avg delivery "
                    f"time: {sup.avg_delivery_days:.1f} days. Avg lateness: "
                    f"{sup.avg_lateness_days:.1f} days. Composite reliability: "
                    f"{sup.reliability:.1f}/100 ({sup.tier})."
                ),
                recommendation=(
                    f"Issue a corrective-action request and split approximately "
                    f"{shiftable_orders} of their upcoming orders (30% of "
                    f"volume) to a more reliable alternate supplier."
                ),
                expected_impact=(
                    f"Restoring on-time delivery to {sup.on_time_pct * 100:.0f}% "
                    f"would prevent roughly "
                    f"{math.ceil(sup.orders * 0.30 * (sup.on_time_pct - sup.recent_on_time_pct))} "
                    f"late POs per quarter and stabilise inventory coverage."
                ),
            )
        )

    return cards


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_recommendations(db: Session, currency: str = "KES") -> RecommendationsResponse:
    inventory = inventory_service.get_inventory(db, currency=currency)
    cashflow = cashflow_service.get_cashflow_forecast(db, currency=currency)
    customers = customer_service.get_customers(db, currency=currency)
    suppliers = supplier_service.get_suppliers(db, currency=currency)

    cards: list[Recommendation] = []
    cards.extend(_inventory_recommendations(inventory))
    cards.extend(_cashflow_recommendations(cashflow))
    cards.extend(_pricing_recommendations(db))
    cards.extend(_customer_recommendations(customers))
    cards.extend(_supplier_recommendations(suppliers))

    # Rank by priority_score descending — most urgent first
    cards.sort(key=lambda c: c.priority_score, reverse=True)

    totals = RecommendationTotals(
        total=len(cards),
        high=sum(1 for c in cards if c.priority == "high"),
        medium=sum(1 for c in cards if c.priority == "medium"),
        low=sum(1 for c in cards if c.priority == "low"),
        by_type={
            t: sum(1 for c in cards if c.type == t)
            for t in ("inventory", "cashflow", "pricing", "customer", "supplier")
        },
    )

    return RecommendationsResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        currency=currency,
        totals=totals,
        cards=cards,
    )