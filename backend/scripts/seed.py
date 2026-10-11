"""
Seed the SME OLTP database with realistic Nairobi agro-supply business data.

    docker compose exec backend alembic upgrade head
    docker compose exec backend python -m scripts.seed

Env:
    DATABASE_URL   postgresql://sme:sme@postgres:5432/sme_oltp
"""
from __future__ import annotations

import os
import random
import uuid
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import psycopg2
import psycopg2.extras 
from psycopg2.extras import execute_values
from faker import Faker

# ---- register the UUID adapter before any DB work ------------------------
psycopg2.extras.register_uuid()
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
fake = Faker(["en_GB", "en_US"])
Faker.seed(SEED)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://sme:sme@localhost:5432/sme_oltp"
)

START_DATE = date(2025, 3, 1)
END_DATE = date(2025, 9, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days + 1

BUSINESS_NAME = "GreenHarvest Agro Supplies"
CURRENCY = "KES"

# (name, region, sales_weight)
BRANCHES = [
    ("Nairobi CBD", "Nairobi", 1.00),
    ("Westlands", "Nairobi", 0.75),
    ("Thika Road", "Kiambu", 0.60),
]

NUM_CUSTOMERS = 380

# Problem-pattern hooks
STOCKOUT_SKU = "TOM-SEED"
DEGRADING_SUPPLIER = "Rift Valley Agro Distributors"
STRESS_WINDOW_DAYS = 45

OPENING_CASH = Decimal("1200000.00")
MIN_SAFE_BALANCE = Decimal("150000.00")

# ---------------------------------------------------------------------------
# Catalogues
# ---------------------------------------------------------------------------
# (name, unit, cost, sell, reorder_point, popularity, tag)
PRODUCT_CATALOG = {
    "Seeds": [
        ("Tomato Seeds",         "packet",   180,   350, 25, 1.0, "STOCKOUT"),
        ("Maize Seeds (Hybrid)", "2kg bag",  450,   780, 15, 1.4, None),
        ("Kale Seeds",           "packet",   120,   240, 20, 1.2, None),
        ("Onion Seeds",          "packet",   200,   390, 15, 1.1, None),
        ("Cabbage Seeds",        "packet",   150,   290, 15, 1.0, None),
        ("Carrot Seeds",         "packet",   170,   330, 12, 0.9, None),
        ("Spinach Seeds",        "packet",   110,   220, 18, 0.8, None),
        ("Bean Seeds",           "2kg bag",  380,   650, 15, 1.1, None),
        ("Pepper Seeds",         "packet",   160,   310, 10, 0.7, None),
        ("Cucumber Seeds",       "packet",   190,   370, 10, 0.6, None),
        ("Watermelon Seeds",     "packet",   210,   400,  8, 0.6, None),
        ("Sunflower Seeds",      "1kg bag",  250,   450, 10, 0.5, None),
    ],
    "Fertilizers": [
        ("DAP 50kg",             "bag",     3200,  4100, 20, 1.6, None),
        ("CAN 50kg",             "bag",     2800,  3600, 20, 1.5, None),
        ("Urea 50kg",            "bag",     3100,  3950, 18, 1.4, None),
        ("NPK 20-20-20",         "bag",     3400,  4300, 15, 1.3, None),
        ("Organic Compost 25kg", "bag",      650,   950, 30, 1.2, None),
        ("Lime 25kg",            "bag",      450,   700, 25, 1.0, None),
        ("TSP 50kg",             "bag",     3000,  3850, 12, 0.9, None),
        ("MOP 50kg",             "bag",     2900,  3750, 12, 0.8, None),
        ("SSP 50kg",             "bag",     2700,  3500, 12, 0.7, None),
        ("Foliar Feed 1L",       "bottle",   850,  1250, 20, 0.9, None),
    ],
    "Pesticides": [
        ("Roundup 1L",           "bottle",   950,  1400, 25, 1.5, None),
        ("Karate 100ml",         "bottle",   420,   680, 30, 1.4, None),
        ("Ridomil 500g",         "pack",     780,  1200, 20, 1.3, None),
        ("Confidor 100ml",       "bottle",   650,   980, 25, 1.2, None),
        ("Dithane 1kg",          "pack",     720,  1100, 20, 1.1, None),
        ("Malathion 500ml",      "bottle",   380,   620, 30, 0.9, None),
        ("Cypermethrin 1L",      "bottle",   560,   880, 25, 1.0, None),
        ("Neem Oil 1L",          "bottle",   690,  1050, 20, 0.9, None),
    ],
    "Farm Tools": [
        ("Jembe (Hoe)",          "unit",     450,   750, 10, 1.3, None),
        ("Panga (Machete)",      "unit",     380,   650, 10, 1.2, None),
        ("Watering Can 10L",     "unit",     550,   900, 12, 1.0, None),
        ("Knapsack Sprayer 16L", "unit",    2800,  4200,  8, 1.4, None),
        ("Wheelbarrow",          "unit",    3200,  4800,  5, 1.0, None),
        ("Hose 20m",             "unit",    1200,  1900, 10, 0.9, None),
        ("Pruning Shears",       "unit",     650,  1050, 12, 1.1, None),
        ("Rake",                 "unit",     420,   700, 10, 0.8, None),
        ("Spade",                "unit",     500,   820, 10, 1.0, None),
        ("Hand Trowel",          "unit",     220,   400, 15, 0.9, None),
    ],
    "Animal Feed": [
        ("Dairy Meal 70kg",      "bag",     2400,  3100, 15, 1.5, None),
        ("Layers Mash 70kg",     "bag",     2300,  2950, 15, 1.4, None),
        ("Broiler Starter 50kg", "bag",     2100,  2700, 12, 1.3, None),
        ("Pig Grower 50kg",      "bag",     2200,  2850, 10, 1.0, None),
        ("Fish Feed 20kg",       "bag",     1800,  2400, 10, 0.8, None),
        ("Rabbit Pellets 20kg",  "bag",     1400,  1900,  8, 0.7, None),
        ("Hay Bale",             "bale",     350,   550, 20, 1.1, None),
        ("Mineral Lick 5kg",     "block",    650,   980, 15, 0.9, None),
    ],
    "Irrigation": [
        ("Drip Kit Small",       "kit",     3500,  5200,  5, 1.0, None),
        ("Drip Kit Medium",      "kit",     7800, 11000,  3, 0.9, None),
        ("Sprinkler Set",        "set",     2400,  3600,  6, 0.8, None),
        ("Water Pump 1HP",       "unit",    9500, 13500,  2, 0.7, None),
        ("PVC Pipe 4m",          "unit",     380,   620, 25, 1.2, None),
        ("Connector Pack",       "pack",     220,   420, 30, 1.1, None),
        ("Filter Unit",          "unit",     850,  1350, 10, 0.7, None),
    ],
}

# (name, country, base_lead_time_days, base_on_time_rate, primary_categories)
SUPPLIER_DEFS = [
    ("Kenya Seed Company",           "Kenya", 3, 0.94, ["Seeds"]),
    ("East African Seeds Ltd",       "Kenya", 4, 0.88, ["Seeds"]),
    ("Western Seed Co.",             "Kenya", 5, 0.82, ["Seeds"]),
    # ↓ problem supplier: on-time degrades in the last ~4 months
    ("Rift Valley Agro Distributors","Kenya", 6, 0.90, ["Seeds", "Fertilizers"]),
    ("Yara East Africa",             "Kenya", 4, 0.95, ["Fertilizers"]),
    ("Mavuno Fertilizers",           "Kenya", 3, 0.91, ["Fertilizers"]),
    ("OCP Africa Kenya",             "Kenya", 6, 0.87, ["Fertilizers"]),
    ("Syngenta Kenya",               "Kenya", 4, 0.93, ["Pesticides"]),
    ("Bayer Crop Science EA",        "Kenya", 5, 0.89, ["Pesticides"]),
    ("Amiran Kenya",                 "Kenya", 4, 0.92, ["Pesticides", "Irrigation"]),
    ("Elgon Kenya Ltd",              "Kenya", 5, 0.85, ["Farm Tools"]),
    ("Farmcare Tools",               "Kenya", 3, 0.90, ["Farm Tools"]),
    ("Kenchic Feeds",                "Kenya", 3, 0.93, ["Animal Feed"]),
    ("Unga Feeds Ltd",               "Kenya", 4, 0.88, ["Animal Feed"]),
    ("Tegemeo Feeds",                "Kenya", 5, 0.80, ["Animal Feed"]),
    ("Netafim Kenya",                "Kenya", 7, 0.86, ["Irrigation"]),
    ("Irri-Max Africa",              "Kenya", 6, 0.82, ["Irrigation"]),
    ("Agri-Hub Supplies",            "Kenya", 4, 0.87, ["Farm Tools", "Irrigation"]),
]

# RFM archetypes: (label, share, active_window, daily_purchase_prob, basket_scale)
CUSTOMER_ARCHETYPES = [
    ("high_value",   0.05, (0, TOTAL_DAYS - 1),   0.55, 1.6),
    ("loyal",        0.15, (0, TOTAL_DAYS - 1),   0.22, 1.2),
    ("potential",    0.15, (30, TOTAL_DAYS - 1),  0.12, 1.0),
    ("new",          0.20, (120, TOTAL_DAYS - 1), 0.06, 0.9),
    ("at_risk",      0.15, (0, TOTAL_DAYS - 60),  0.20, 1.1),
    ("hibernating",  0.15, (0, TOTAL_DAYS - 100), 0.09, 0.9),
    ("lost",         0.15, (0, TOTAL_DAYS - 160), 0.03, 0.8),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def bulk_insert(cur, table, columns, rows, page_size=1000):
    if not rows:
        return
    cols = ", ".join(columns)
    template = "(" + ", ".join(["%s"] * len(columns)) + ")"
    sql = f"INSERT INTO {table} ({cols}) VALUES %s"
    execute_values(cur, sql, rows, template=template, page_size=page_size)


def reset(cur):
    cur.execute("""
        TRUNCATE cash_accounts, payments, purchase_orders,
                 inventory_movements, sale_items, sales,
                 products, customers, suppliers, users, branches, businesses
        RESTART IDENTITY CASCADE;
    """)


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
def insert_reference_data(cur):
    business_id = uuid.uuid4()
    cur.execute(
        "INSERT INTO businesses (id, name, country, base_currency) VALUES (%s,%s,%s,%s)",
        (business_id, BUSINESS_NAME, "Kenya", CURRENCY),
    )

    branch_ids = []
    branch_weights = []
    for name, location, w in BRANCHES:
        bid = uuid.uuid4()
        branch_ids.append(bid)
        branch_weights.append(w)
        cur.execute(
            "INSERT INTO branches (id, business_id, name, location) VALUES (%s,%s,%s,%s)",
            (bid, business_id, name, location),
        )

    # demo users
    for email, role in [
        ("owner@greenharvest.co.ke", "owner"),
        ("manager@greenharvest.co.ke", "manager"),
        ("analyst@greenharvest.co.ke", "analyst"),
    ]:
        cur.execute(
            "INSERT INTO users (business_id, email, password_hash, role) VALUES (%s,%s,%s,%s)",
            (business_id, email, "PLACEHOLDER_HASH", role),
        )

    # suppliers
    suppliers = []
    suppliers_by_cat = defaultdict(list)
    for name, country, lt, ot, cats in SUPPLIER_DEFS:
        sid = uuid.uuid4()
        suppliers.append({
            "id": sid, "name": name, "country": country,
            "base_lead_time_days": lt, "base_on_time_rate": ot, "cats": cats,
        })
        for c in cats:
            suppliers_by_cat[c].append(sid)
        cur.execute(
            "INSERT INTO suppliers (id, business_id, name, contact, country) VALUES (%s,%s,%s,%s,%s)",
            (sid, business_id, name, fake.company_email(), country),
        )
    supplier_by_id = {s["id"]: s for s in suppliers}

    # products
    products = []
    for category, entries in PRODUCT_CATALOG.items():
        for name, unit, cost, sell, rop, pop, tag in entries:
            sku = "".join(w[0] for w in name.split()[:3]).upper() + "-" + str(len(products) + 1).zfill(3)
            # assign a supplier that carries this category, otherwise random
            pool = suppliers_by_cat.get(category) or [s["id"] for s in suppliers]
            sup_id = random.choice(pool)
            sup = supplier_by_id[sup_id]
            pid = uuid.uuid4()
            products.append({
                "id": pid, "sku": sku, "name": name, "category": category,
                "unit": unit, "cost_price": cost, "sell_price": sell,
                "reorder_point": rop, "lead_time_days": sup["base_lead_time_days"],
                "popularity": pop, "tag": tag, "supplier": sup,
            })
            cur.execute(
                """INSERT INTO products
                   (id, business_id, sku, name, category, unit,
                    cost_price, sell_price, reorder_point, lead_time_days, supplier_id)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (pid, business_id, sku, name, category, unit,
                 cost, sell, rop, sup["base_lead_time_days"], sup_id),
            )

    # customers — distributed across archetypes
    customers = []
    counts = _allocate_shares(NUM_CUSTOMERS, [a[1] for a in CUSTOMER_ARCHETYPES])
    for (archetype, _, window, base_prob, basket_scale), n in zip(CUSTOMER_ARCHETYPES, counts):
        for _ in range(n):
            cid = uuid.uuid4()
            start_off = max(0, window[0] + random.randint(-5, 15))
            end_off = min(TOTAL_DAYS - 1, window[1] + random.randint(-10, 5))
            if end_off < start_off:
                end_off = start_off
            customers.append({
                "id": cid,
                "archetype": archetype,
                "start": START_DATE + timedelta(days=start_off),
                "end": START_DATE + timedelta(days=end_off),
                "base_prob": base_prob * random.uniform(0.7, 1.4),
                "basket_scale": basket_scale,
            })
            cur.execute(
                """INSERT INTO customers (id, business_id, name, phone, email, segment)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (cid, business_id, fake.name(), fake.msisdn()[:12],
                 fake.unique.email(), archetype),
            )

    return {
        "business_id": business_id,
        "branch_ids": branch_ids,
        "branch_weights": branch_weights,
        "suppliers": suppliers,
        "products": products,
        "customers": customers,
    }


def _allocate_shares(total, shares):
    """Turn fractions into integer counts that sum to `total`."""
    counts = [int(round(total * s)) for s in shares]
    diff = total - sum(counts)
    counts[0] += diff
    return counts


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def simulate(refs):
    business_id = refs["business_id"]
    branch_ids = refs["branch_ids"]
    branch_weights = refs["branch_weights"]
    products = refs["products"]
    customers = refs["customers"]
    supplier_by_id = {s["id"]: s for s in refs["suppliers"]}

    sales_rows = []
    sale_items_rows = []
    inv_mov_rows = []
    po_rows = []
    payment_rows = []

    # ---- opening stock and opening cash account ------------------------------
    stock = {}  # (branch_id, product_id) -> qty
    for bid in branch_ids:
        for p in products:
            opening = p["reorder_point"] * 3 + random.randint(0, p["reorder_point"])
            stock[(bid, p["id"])] = opening

    # ---- main loop -----------------------------------------------------------
    pending_pos = []          # [{...}] with `due_date`
    po_lookup = {}            # po_id -> dict (for updating received_date)

    for day_offset in range(TOTAL_DAYS):
        today = START_DATE + timedelta(days=day_offset)
        is_weekend = today.weekday() >= 5
        is_payday = today.day in (1, 15, 28, 29, 30, 31)
        planting_season = today.month in (3, 4, 5, 9, 10)

        # 1. Receive POs that are due today
        still_pending = []
        for po in pending_pos:
            if po["due_date"] <= today:
                key = (po["branch_id"], po["product_id"])
                stock[key] = stock.get(key, 0) + po["qty"]
                inv_mov_rows.append((
                    uuid.uuid4(), business_id, po["branch_id"], po["product_id"],
                    "in", po["qty"],
                    datetime.combine(po["due_date"], time(8, 0)),
                    str(po["id"]),
                ))
                po_lookup[po["id"]]["received_date"] = datetime.combine(po["due_date"], time(8, 0))
                po_lookup[po["id"]]["status"] = "received"
            else:
                still_pending.append(po)
        pending_pos = still_pending

        # 2. Customers available today
        active_customers = [
            c for c in customers if c["start"] <= today <= c["end"]
        ]
        active_weights = [c["base_prob"] for c in active_customers]

        # 3. Product popularity for today (tomato seeds grow over time)
        if planting_season:
            season_boost = 1.25
        else:
            season_boost = 1.0

        product_weights = []
        for p in products:
            w = p["popularity"]
            if p["sku"].startswith("TOM") or p["tag"] == "STOCKOUT":
                # grow from 1.0× → 3.0× over the window
                w *= (1.0 + 2.0 * day_offset / TOTAL_DAYS)
            product_weights.append(w * season_boost)

        # 4. Sales
        for bid, bw in zip(branch_ids, branch_weights):
            n_sales = max(0, int(random.gauss(15 * bw, 3)))
            if is_weekend:
                n_sales = int(n_sales * 1.30)
            if is_payday:
                n_sales = int(n_sales * 1.35)
            n_sales = int(n_sales * season_boost)

            for _ in range(n_sales):
                if not active_customers:
                    continue
                cust = random.choices(active_customers, weights=active_weights, k=1)[0]

                # pick 1–4 distinct products
                n_items = random.choices(
                    [1, 2, 3, 4], weights=[0.45, 0.30, 0.15, 0.10], k=1
                )[0]
                chosen = []
                attempts = 0
                while len(chosen) < n_items and attempts < 8:
                    attempts += 1
                    p = random.choices(products, weights=product_weights, k=1)[0]
                    if p["id"] not in {c["id"] for c in chosen}:
                        chosen.append(p)
                if not chosen:
                    continue

                sale_id = uuid.uuid4()
                sale_dt = datetime.combine(
                    today, time(random.randint(8, 18), random.randint(0, 59))
                )

                total = Decimal("0")
                discount_total = Decimal("0")
                for p in chosen:
                    # basket scale varies by customer archetype
                    scale = cust["basket_scale"]
                    if p["sell_price"] > 3000:
                        qty = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10], k=1)[0]
                    else:
                        base_qty = random.choices(
                            [1, 2, 3, 4, 5, 8, 10],
                            weights=[0.42, 0.24, 0.14, 0.08, 0.06, 0.04, 0.02],
                            k=1,
                        )[0]
                        qty = max(1, int(round(base_qty * scale)))

                    unit_price = Decimal(str(p["sell_price"]))
                    if random.random() < 0.15:
                        disc = unit_price * Decimal(str(random.choice([0.05, 0.10])))
                        discount_total += disc * qty
                        unit_price -= disc

                    total += unit_price * qty
                    sale_items_rows.append((
                        uuid.uuid4(), sale_id, p["id"], qty,
                        unit_price, Decimal(str(p["cost_price"])),
                    ))

                    # decrement stock (never below 0)
                    key = (bid, p["id"])
                    stock[key] = max(0, stock.get(key, 0) - qty)
                    inv_mov_rows.append((
                        uuid.uuid4(), business_id, bid, p["id"],
                        "out", qty, sale_dt, str(sale_id),
                    ))

                # status
                r = random.random()
                status = "paid" if r < 0.78 else ("pending" if r < 0.97 else "cancelled")

                sales_rows.append((
                    sale_id, business_id, bid, cust["id"], sale_dt,
                    CURRENCY, total, discount_total, status,
                ))

                if status == "paid":
                    payment_rows.append((
                        uuid.uuid4(), business_id, sale_id, None, "in",
                        total, CURRENCY,
                        sale_dt + timedelta(minutes=random.randint(0, 45)),
                        random.choice(["cash", "mpesa", "card", "bank"]),
                    ))

        # 5. Weekly restock check (every Monday)
        if today.weekday() == 0:
            for bid in branch_ids:
                for p in products:
                    key = (bid, p["id"])
                    qty = stock.get(key, 0)
                    if qty >= p["reorder_point"]:
                        continue

                    target = p["reorder_point"] * 3
                    order_qty = max(p["reorder_point"], target - qty)

                    # PROBLEM: under-order tomato seeds so it trends toward stockout
                    if p["tag"] == "STOCKOUT":
                        order_qty = max(1, int(round(order_qty * 0.35)))

                    sup = p["supplier"]
                    base_lt = sup["base_lead_time_days"]

                    if sup["name"] == DEGRADING_SUPPLIER:
                        # lead time inflates over the last 4 months
                        deg = max(0.0, (day_offset - (TOTAL_DAYS - 120)) / 120.0)
                        lead_time = max(
                            1, base_lt + int(round(3 * deg)) + random.randint(-1, 2)
                        )
                        on_time = max(0.50, sup["base_on_time_rate"] - 0.35 * deg)
                    else:
                        lead_time = max(1, base_lt + random.randint(-1, 2))
                        on_time = sup["base_on_time_rate"]

                    order_dt = datetime.combine(today, time(10, 0))
                    expected_dt = datetime.combine(
                        today + timedelta(days=lead_time), time(9, 0)
                    )

                    if random.random() > on_time:
                        slip = random.randint(1, 5)
                        due_date = today + timedelta(days=lead_time + slip)
                    else:
                        due_date = today + timedelta(days=lead_time)

                    po_id = uuid.uuid4()
                    po_row = {
                        "id": po_id, "business_id": business_id,
                        "supplier_id": sup["id"], "product_id": p["id"],
                        "quantity": order_qty,
                        "unit_cost": Decimal(str(p["cost_price"])),
                        "order_date": order_dt,
                        "expected_date": expected_dt,
                        "received_date": None,
                        "status": "open",
                    }
                    po_rows.append(po_row)
                    po_lookup[po_id] = po_row
                    pending_pos.append({
                        "id": po_id, "branch_id": bid, "product_id": p["id"],
                        "qty": order_qty, "due_date": due_date,
                    })

                    # pay supplier on order date
                    payment_rows.append((
                        uuid.uuid4(), business_id, None, po_id, "out",
                        po_row["unit_cost"] * order_qty, CURRENCY, order_dt,
                        random.choice(["bank", "mpesa", "cheque"]),
                    ))

        # 6. Recurring expenses
        if today.day == 1:
            payment_rows.append(_expense(business_id, "rent", Decimal("180000"), today, "bank"))
        if today.day == 5:
            payment_rows.append(_expense(business_id, "utilities", Decimal("35000"), today, "mpesa"))
            payment_rows.append(_expense(business_id, "internet", Decimal("12000"), today, "mpesa"))
        if today.day == 15:
            payment_rows.append(_expense(business_id, "marketing", Decimal("40000"), today, "bank"))
        if today.day == 28:
            payment_rows.append(_expense(business_id, "salaries", Decimal("420000"), today, "bank"))

    # ---- one-off stress outflows in the last STRESS_WINDOW_DAYS -------------
    stress_start = END_DATE - timedelta(days=STRESS_WINDOW_DAYS)
    payment_rows.append(_expense(
        business_id, "bulk_inventory_prepayment", Decimal("1200000"),
        stress_start + timedelta(days=5), "bank",
    ))
    payment_rows.append(_expense(
        business_id, "vehicle_deposit", Decimal("1500000"),
        stress_start + timedelta(days=22), "bank",
    ))
    payment_rows.append(_expense(
        business_id, "quarterly_tax", Decimal("650000"),
        stress_start + timedelta(days=33), "bank",
    ))

    # ---- convert PO dicts to tuples -----------------------------------------
    po_tuples = [
        (r["id"], r["business_id"], r["supplier_id"], r["product_id"],
         r["quantity"], r["unit_cost"], r["order_date"],
         r["expected_date"], r["received_date"], r["status"])
        for r in po_rows
    ]

    # ---- final cash balance --------------------------------------------------
    total_in = sum(p[5] for p in payment_rows if p[4] == "in")
    total_out = sum(p[5] for p in payment_rows if p[4] == "out")
    ending_balance = OPENING_CASH + total_in - total_out

    return {
        "sales": sales_rows,
        "sale_items": sale_items_rows,
        "inventory_movements": inv_mov_rows,
        "purchase_orders": po_tuples,
        "payments": payment_rows,
        "ending_balance": ending_balance,
        "stock": stock,
        "open_pos": pending_pos,
    }


def _expense(business_id, method, amount, when, pay_method):
    dt = datetime.combine(when, time(9, 0))
    return (uuid.uuid4(), business_id, None, None, "out", amount, CURRENCY, dt,
            f"{pay_method}:{method}")


# ---------------------------------------------------------------------------
# Persist
# ---------------------------------------------------------------------------
def insert_transactional_data(cur, refs, data):
    business_id = refs["business_id"]

    bulk_insert(cur, "sales",
        ["id", "business_id", "branch_id", "customer_id", "sale_date",
         "currency", "total_amount", "discount", "status"],
        data["sales"])

    bulk_insert(cur, "sale_items",
        ["id", "sale_id", "product_id", "quantity", "unit_price", "unit_cost"],
        data["sale_items"])

    bulk_insert(cur, "inventory_movements",
        ["id", "business_id", "branch_id", "product_id", "movement_type",
         "quantity", "movement_date", "reference"],
        data["inventory_movements"])

    bulk_insert(cur, "purchase_orders",
        ["id", "business_id", "supplier_id", "product_id", "quantity",
         "unit_cost", "order_date", "expected_date", "received_date", "status"],
        data["purchase_orders"])

    bulk_insert(cur, "payments",
        ["id", "business_id", "sale_id", "purchase_order_id", "direction",
         "amount", "currency", "payment_date", "method"],
        data["payments"])

    # cash accounts — split ending balance across the three branches
    balance = data["ending_balance"]
    splits = [Decimal("0.55"), Decimal("0.30"), Decimal("0.15")]
    for bid, s in zip(refs["branch_ids"], splits):
        cur.execute(
            """INSERT INTO cash_accounts
               (business_id, branch_id, balance, currency, min_safe_balance)
               VALUES (%s,%s,%s,%s,%s)""",
            (business_id, bid, (balance * s).quantize(Decimal("0.01")),
             CURRENCY, MIN_SAFE_BALANCE),
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print(f"→ connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        print("→ resetting tables")
        reset(cur)

        print("→ inserting reference data")
        refs = insert_reference_data(cur)

        print(f"→ simulating {TOTAL_DAYS} days of activity "
              f"({len(refs['products'])} products, "
              f"{len(refs['customers'])} customers, "
              f"{len(refs['branch_ids'])} branches)")
        data = simulate(refs)

        print("→ persisting transactions")
        insert_transactional_data(cur, refs, data)

        conn.commit()

        print()
        print("=" * 68)
        print("  SEED COMPLETE")
        print("=" * 68)
        print(f"  branches       : {len(refs['branch_ids'])}")
        print(f"  suppliers      : {len(refs['suppliers'])}")
        print(f"  products       : {len(refs['products'])}")
        print(f"  customers      : {len(refs['customers'])}")
        print(f"  sales          : {len(data['sales']):>8,}")
        print(f"  sale items     : {len(data['sale_items']):>8,}")
        print(f"  inventory moves: {len(data['inventory_movements']):>8,}")
        print(f"  purchase orders: {len(data['purchase_orders']):>8,}")
        print(f"  payments       : {len(data['payments']):>8,}")
        print(f"  ending cash    : {data['ending_balance']:>12,.2f} {CURRENCY}")
        print(f"  min safe bal.  : {MIN_SAFE_BALANCE:>12,.2f} {CURRENCY}")
        if data["ending_balance"] < MIN_SAFE_BALANCE * 2:
            print("  ⚠  cash balance is trending toward the minimum threshold")
        print("=" * 68)
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()