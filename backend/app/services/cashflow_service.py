from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.cashflow import (
    CashflowForecastResponse,
    CashflowPoint,
    CashflowSummary,
    ShortageAlert,
)


def _t(name: str) -> str:
    """Return a schema-qualified table name based on the warehouse flag."""
    return (
        f"{settings.warehouse_schema}.{name}"
        if settings.warehouse_enabled
        else f"public.{name}"
    )


RECURRING_METHODS = {
    "bank:rent",
    "mpesa:utilities",
    "mpesa:internet",
    "bank:marketing",
    "bank:salaries",
}

STRESS_METHODS = {
    "bank:bulk_inventory_prepayment",
    "bank:vehicle_deposit",
    "bank:quarterly_tax",
}


def _recurring_for_day(d: date) -> float:
    total = 0.0
    if d.day == 1:
        total += 180_000.0
    if d.day == 5:
        total += 35_000.0 + 12_000.0
    if d.day == 15:
        total += 40_000.0
    if d.day == 28:
        total += 420_000.0
    return total


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    var = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return var ** 0.5


def get_cashflow_forecast(
    db: Session,
    horizon_days: int = 30,
    currency: str = "KES",
) -> CashflowForecastResponse:
    # ---- Current cash (always OLTP) -------------------------------------
    cash_row = db.execute(
        text(
            """
            SELECT COALESCE(SUM(balance), 0)::float       AS current_cash,
                   COALESCE(MAX(min_safe_balance), 150000)::float AS min_safe
            FROM cash_accounts
            """
        )
    ).mappings().one()

    current_cash = float(cash_row["current_cash"] or 0.0)
    min_safe = float(cash_row["min_safe"] or 150_000.0)

    # ---- Anchor date ----------------------------------------------------
    if settings.warehouse_enabled:
        last_date = db.execute(
            text(
                f"""
                SELECT GREATEST(
                    COALESCE((SELECT MAX(sale_date)::date FROM {_t('fact_sales')}), CURRENT_DATE),
                    COALESCE((SELECT MAX(payment_date)::date FROM {_t('fact_payments')}), CURRENT_DATE)
                ) AS d
                """
            )
        ).scalar()
    else:
        last_date = db.execute(
            text(
                """
                SELECT GREATEST(
                    COALESCE((SELECT MAX(sale_date)::date FROM sales), CURRENT_DATE),
                    COALESCE((SELECT MAX(payment_date)::date FROM payments), CURRENT_DATE)
                ) AS d
                """
            )
        ).scalar()

    if last_date is None:
        last_date = date.today()

    # ---- Historical daily flows -----------------------------------------
    if settings.warehouse_enabled:
        flow_rows = db.execute(
            text(
                f"""
                SELECT payment_date::date AS date,
                       direction,
                       amount::float AS amount,
                       COALESCE(method, '') AS method
                FROM {_t('fact_payments')}
                WHERE payment_date >= :since
                ORDER BY payment_date
                """
            ),
            {"since": last_date - timedelta(days=60)},
        ).mappings().all()
    else:
        flow_rows = db.execute(
            text(
                """
                SELECT payment_date::date AS date,
                       direction,
                       amount::float AS amount,
                       COALESCE(method, '') AS method
                FROM payments
                WHERE payment_date >= :since
                ORDER BY payment_date
                """
            ),
            {"since": last_date - timedelta(days=60)},
        ).mappings().all()

    daily_in: dict[date, float] = {}
    daily_out_baseline: dict[date, float] = {}

    for r in flow_rows:
        d: date = r["date"]
        amt: float = r["amount"]
        direction: str = r["direction"]
        method: str = r["method"]

        if direction == "in":
            daily_in[d] = daily_in.get(d, 0.0) + amt
        else:
            if method in RECURRING_METHODS or method in STRESS_METHODS:
                continue
            daily_out_baseline[d] = daily_out_baseline.get(d, 0.0) + amt

    baseline_in = _median(list(daily_in.values()))
    baseline_out = _median(list(daily_out_baseline.values()))

    all_days = set(daily_in) | set(daily_out_baseline)
    daily_nets = [
        daily_in.get(d, 0.0) - daily_out_baseline.get(d, 0.0) for d in all_days
    ]
    noise_std = _stdev(daily_nets)

    # ---- Outstanding receivables ----------------------------------------
    if settings.warehouse_enabled:
        pending_receivables = float(
            db.execute(
                text(
                    f"""
                    SELECT COALESCE(SUM(revenue), 0)::float
                    FROM {_t('fact_sales')}
                    WHERE status = 'pending'
                    """
                )
            ).scalar()
            or 0.0
        )
    else:
        pending_receivables = float(
            db.execute(
                text(
                    """
                    SELECT COALESCE(SUM(total_amount), 0)::float
                    FROM sales
                    WHERE status = 'pending'
                    """
                )
            ).scalar()
            or 0.0
        )

    receivable_daily = pending_receivables / 14.0

    # ---- Project forward ------------------------------------------------
    forecast: list[CashflowPoint] = []
    balance = current_cash
    total_inflow = 0.0
    total_outflow = 0.0

    for step in range(1, horizon_days + 1):
        d = last_date + timedelta(days=step)

        inflow = baseline_in + (receivable_daily if step <= 14 else 0.0)
        outflow = baseline_out + _recurring_for_day(d)
        net = inflow - outflow
        balance += net

        band = 1.28 * noise_std * (step ** 0.5)
        band = max(band, 0.0)

        total_inflow += inflow
        total_outflow += outflow

        forecast.append(
            CashflowPoint(
                date=d.isoformat(),
                balance=round(balance, 2),
                lower=round(balance - band, 2),
                upper=round(balance + band, 2),
                inflow=round(inflow, 2),
                outflow=round(outflow, 2),
            )
        )

    # ---- Shortage alert -------------------------------------------------
    alert: ShortageAlert | None = None
    first_breach_idx: int | None = None
    for i, point in enumerate(forecast):
        if point.balance < min_safe:
            first_breach_idx = i
            break

    if first_breach_idx is not None:
        min_balance = min(p.balance for p in forecast)
        breach_date = forecast[first_breach_idx].date

        shortfall = max(0.0, min_safe - min_balance)
        if shortfall < min_safe * 0.20:
            recommendation = (
                "Tighten discretionary spending over the next two weeks and "
                "follow up on the oldest outstanding invoices."
            )
        elif shortfall < min_safe * 0.75:
            recommendation = (
                "Delay non-essential purchases or accelerate outstanding "
                "receivables to stay above the minimum safe balance."
            )
        else:
            recommendation = (
                "Immediate action required: pursue outstanding receivables "
                "aggressively and defer all non-critical outflows."
            )

        alert = ShortageAlert(
            predicted_date=breach_date,
            expected_minimum=round(min_balance, 2),
            minimum_safe_balance=round(min_safe, 2),
            recommendation=recommendation,
        )

    summary = CashflowSummary(
        current_cash=round(current_cash, 2),
        expected_income=round(total_inflow, 2),
        expected_expenses=round(total_outflow, 2),
        predicted_min_balance=round(min(p.balance for p in forecast), 2),
        min_safe_balance=round(min_safe, 2),
        currency=currency,
    )

    return CashflowForecastResponse(
        summary=summary,
        forecast=forecast,
        alert=alert,
    )