# PROJECT_PLAN.md

**Project:** SME Financial & Supply-Chain Intelligence Platform
**Owner:** Portfolio project
**Audience:** African SMEs (retail, agro-inputs, FMCG distribution)
**Purpose:** Transform raw business transactions into actionable decision intelligence.

> This file is the single source of truth for the project. All future work must remain consistent with it unless an explicit change is requested.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Monorepo Folder Structure](#3-monorepo-folder-structure)
4. [OLTP Schema (PostgreSQL)](#4-oltp-schema-postgresql)
5. [Data Warehouse Schema](#5-data-warehouse-schema)
6. [Airflow Architecture](#6-airflow-architecture)
7. [dbt Architecture](#7-dbt-architecture)
8. [ML Architecture](#8-ml-architecture)
9. [API Specification](#9-api-specification)
10. [UI Page Hierarchy & Routes](#10-ui-page-hierarchy--routes)
11. [Design System](#11-design-system)
12. [Seed Data Contract](#12-seed-data-contract)
13. [Localization & Multi-Tenancy](#13-localization--multi-tenancy)
14. [Development Roadmap](#14-development-roadmap)
15. [Conventions](#15-conventions)
16. [Definition of Done](#16-definition-of-done)

---

## 1. Overview

An analytics and decision-support platform for African small and medium-sized businesses. It combines:

- Sales analytics
- Inventory management
- Supplier analytics
- Customer analytics
- Cash-flow forecasting
- Demand forecasting
- Inventory forecasting
- Customer segmentation
- Business intelligence

**Not** a generic accounting dashboard. The product surface is a **decision-intelligence platform**: raw transactions in, ranked recommendations out.

**Reference business for demo data:** *GreenHarvest Agro Supplies* — a Nairobi agro-inputs retailer with 3 branches, 55 products across 6 categories, ~18 suppliers, 380 customers.

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                 CLIENT LAYER                                 │
│  React + Vite + TS + MUI + React Router   (premium BI/fintech aesthetic)     │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │ HTTPS / JSON
┌────────────────────────────────────▼─────────────────────────────────────────┐
│                              API LAYER (FastAPI)                             │
│  /dashboard /sales /inventory /customers /suppliers                          │
│  /forecast/demand /forecast/cashflow /recommendations                        │
│  Auth (JWT), currency middleware (KES/USD), branch context                   │
└──────┬───────────────────────┬───────────────────────┬───────────────────────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌─────────────┐        ┌────────────────┐       ┌──────────────────┐
│  OLTP DB    │        │  WAREHOUSE     │       │   ML SERVING     │
│ PostgreSQL  │        │  PostgreSQL    │       │  (FastAPI router │
│ (raw writes)│        │  (dims+facts)  │       │   + MLflow reg.) │
└──────┬──────┘        └───────▲────────┘       └────────▲─────────┘
       │                       │                         │
       │        ┌──────────────┴───────────┐   ┌─────────┴──────────┐
       │        │   dbt (staging→marts)    │   │  MLflow Tracking   │
       │        └──────────────▲───────────┘   │  Model Registry    │
       │                       │               └─────────▲──────────┘
       │        ┌──────────────┴───────────┐             │
       └───────►│  Apache Airflow (DAGs)   ├─────────────┘
                │  ingest → spark → dbt    │
                │  → warehouse → ml train  │
                └──────────────┬───────────┘
                               │
                       ┌───────▼────────┐
                       │  Apache Spark  │
                       │  (cleaning,    │
                       │   feature eng) │
                       └────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Raw sources (CSV/S3/ │
                    │ POS/ERP mock feeds)  │
                    └──────────────────────┘
```

**Principles**

- OLTP is never read by analytics queries. All analytics read from warehouse marts.
- ML features are derived from warehouse marts — never re-derived in notebooks.
- Everything is containerized: `docker compose up` boots the whole stack.
- Every business entity carries `business_id` so multi-tenancy is a filter, not a refactor.
- Every monetary value is stored with an explicit `currency` column; conversions happen at the presentation layer.

---

## 3. Monorepo Folder Structure

```
sme-intelligence/
├── README.md
├── PROJECT_PLAN.md                  # this file
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
│
├── frontend/                        # React + Vite + TS + MUI
│   ├── src/
│   │   ├── app/                     # router, providers
│   │   ├── components/              # KpiCard, ChartCard, RecommendationCard
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   ├── sales/
│   │   │   ├── inventory/
│   │   │   ├── demand-forecast/
│   │   │   ├── cashflow/
│   │   │   ├── customers/
│   │   │   ├── suppliers/
│   │   │   └── recommendations/
│   │   ├── api/                     # typed fetch client
│   │   ├── hooks/
│   │   ├── lib/                     # currency, date, format
│   │   ├── types/
│   │   ├── theme.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── package.json
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
│
├── backend/                         # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                    # config, security, currency
│   │   ├── db/                      # session, base
│   │   ├── models/                  # OLTP ORM
│   │   ├── schemas/                 # Pydantic
│   │   ├── api/v1/
│   │   │   ├── dashboard.py
│   │   │   ├── sales.py
│   │   │   ├── inventory.py
│   │   │   ├── customers.py
│   │   │   ├── suppliers.py
│   │   │   ├── forecast_demand.py
│   │   │   ├── forecast_cashflow.py
│   │   │   └── recommendations.py
│   │   ├── services/
│   │   └── ml_client.py
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_initial_oltp.py
│   ├── scripts/
│   │   └── seed.py
│   ├── tests/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
│
├── data-eng/
│   ├── airflow/
│   │   ├── dags/
│   │   │   ├── ingest_sales.py
│   │   │   ├── ingest_inventory.py
│   │   │   ├── ingest_customers.py
│   │   │   ├── transform_data.py
│   │   │   ├── build_warehouse.py
│   │   │   └── train_forecasting_models.py
│   │   ├── plugins/
│   │   └── Dockerfile
│   ├── spark/
│   │   ├── jobs/
│   │   │   ├── clean_sales.py
│   │   │   ├── clean_inventory.py
│   │   │   └── feature_engineering.py
│   │   └── Dockerfile
│   ├── dbt/
│   │   ├── dbt_project.yml
│   │   ├── profiles.yml
│   │   ├── models/
│   │   │   ├── staging/
│   │   │   │   ├── stg_sales.sql
│   │   │   │   ├── stg_sale_items.sql
│   │   │   │   ├── stg_inventory.sql
│   │   │   │   ├── stg_customers.sql
│   │   │   │   ├── stg_suppliers.sql
│   │   │   │   ├── stg_products.sql
│   │   │   │   ├── stg_payments.sql
│   │   │   │   └── stg_purchase_orders.sql
│   │   │   └── marts/
│   │   │       ├── dims/
│   │   │       │   ├── dim_customer.sql
│   │   │       │   ├── dim_product.sql
│   │   │       │   ├── dim_supplier.sql
│   │   │       │   ├── dim_location.sql
│   │   │       │   └── dim_date.sql
│   │   │       ├── facts/
│   │   │       │   ├── fact_sales.sql
│   │   │       │   ├── fact_inventory.sql
│   │   │       │   ├── fact_payments.sql
│   │   │       │   └── fact_purchase_orders.sql
│   │   │       ├── mart_daily_revenue.sql
│   │   │       ├── mart_product_demand_daily.sql
│   │   │       ├── mart_customer_rfm.sql
│   │   │       ├── mart_supplier_scorecard.sql
│   │   │       └── mart_cashflow_daily.sql
│   │   └── tests/
│   │       ├── assert_positive_quantity.sql
│   │       ├── assert_no_negative_stock.sql
│   │       └── assert_revenue_matches_items.sql
│   └── seeds/
│
├── ml/
│   ├── src/
│   │   ├── features/
│   │   ├── models/
│   │   │   ├── demand_forecast.py
│   │   │   ├── cashflow_forecast.py
│   │   │   └── customer_segmentation.py
│   │   ├── training/
│   │   ├── evaluation/
│   │   ├── serving/
│   │   │   └── main.py
│   │   └── registry.py
│   ├── notebooks/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
└── infra/
    ├── docker/
    ├── postgres/
    │   ├── init_oltp.sql
    │   └── init_dw.sql
    ├── mlflow/
    │   └── Dockerfile
    ├── nginx/
    │   └── nginx.conf
    └── ci/
        └── github-actions.yml
```

---

## 4. OLTP Schema (PostgreSQL)

**Database:** `sme_oltp`
**Migrations:** Alembic. Migration `0001_initial_oltp` is the canonical definition.

```sql
-- Tenancy & org -------------------------------------------------------------
businesses(
  id UUID PK DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  country TEXT,
  base_currency TEXT NOT NULL DEFAULT 'KES',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

branches(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  name TEXT NOT NULL,
  location TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
-- idx: (business_id)

users(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT CHECK (role IN ('owner','manager','analyst')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

-- Master data ---------------------------------------------------------------
suppliers(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  name TEXT NOT NULL,
  contact TEXT,
  country TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

customers(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  name TEXT,
  phone TEXT,
  email TEXT,
  segment TEXT,                              -- populated by ML in Slice 4
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)

products(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  sku TEXT NOT NULL,
  name TEXT NOT NULL,
  category TEXT,
  unit TEXT,
  cost_price NUMERIC(14,2),
  sell_price NUMERIC(14,2),
  reorder_point INT NOT NULL DEFAULT 0,
  lead_time_days INT NOT NULL DEFAULT 3,
  supplier_id UUID FK → suppliers.id,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (business_id, sku)
)

-- Transactions --------------------------------------------------------------
sales(
  id UUID PK,
  business_id UUID FK → businesses.id ON DELETE CASCADE,
  branch_id UUID FK → branches.id,
  customer_id UUID FK → customers.id NULL,
  sale_date TIMESTAMPTZ NOT NULL,
  currency TEXT NOT NULL,
  total_amount NUMERIC(14,2) NOT NULL,
  discount NUMERIC(14,2) NOT NULL DEFAULT 0,
  status TEXT CHECK (status IN ('paid','pending','cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
-- idx: (business_id, sale_date), (branch_id, sale_date), (customer_id), (status)

sale_items(
  id UUID PK,
  sale_id UUID FK → sales.id ON DELETE CASCADE,
  product_id UUID FK → products.id,
  quantity INT NOT NULL,
  unit_price NUMERIC(14,2) NOT NULL,
  unit_cost NUMERIC(14,2) NOT NULL
)
-- idx: (sale_id), (product_id)

inventory_movements(
  id UUID PK,
  business_id UUID FK,
  branch_id UUID FK,
  product_id UUID FK,
  movement_type TEXT CHECK (movement_type IN ('in','out','adjust')),
  quantity INT NOT NULL,
  movement_date TIMESTAMPTZ NOT NULL,
  reference TEXT
)
-- idx: (business_id, movement_date), (branch_id, product_id)

purchase_orders(
  id UUID PK,
  business_id UUID FK,
  supplier_id UUID FK,
  product_id UUID FK,
  quantity INT NOT NULL,
  unit_cost NUMERIC(14,2) NOT NULL,
  order_date TIMESTAMPTZ NOT NULL,
  expected_date TIMESTAMPTZ,
  received_date TIMESTAMPTZ NULL,
  status TEXT CHECK (status IN ('open','received','cancelled'))
)
-- idx: (business_id, order_date), (supplier_id), (product_id)

payments(
  id UUID PK,
  business_id UUID FK,
  sale_id UUID FK NULL,
  purchase_order_id UUID FK NULL,
  direction TEXT CHECK (direction IN ('in','out')),
  amount NUMERIC(14,2) NOT NULL,
  currency TEXT NOT NULL,
  payment_date TIMESTAMPTZ NOT NULL,
  method TEXT
)
-- idx: (business_id, payment_date), (direction)

cash_accounts(
  id UUID PK,
  business_id UUID FK,
  branch_id UUID FK,
  balance NUMERIC(14,2) NOT NULL,
  currency TEXT NOT NULL,
  min_safe_balance NUMERIC(14,2) NOT NULL DEFAULT 150000,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
```

**Key relationships**

- `businesses 1─N branches`, `users`, `customers`, `suppliers`, `products`
- `sales 1─N sale_items`
- `products N─1 suppliers`
- `payments` links to either `sales` or `purchase_orders`

---

## 5. Data Warehouse Schema

**Database:** `sme_dw` (star schema, built by dbt from `sme_oltp` via Spark-curated staging tables)

### Dimensions

```
dim_customer(customer_key PK, customer_id, business_id, name, segment, first_seen, last_seen)
dim_product(product_key PK, product_id, sku, name, category, unit, supplier_key,
            cost_price, sell_price)
dim_supplier(supplier_key PK, supplier_id, name, country, avg_lead_time_days)
dim_location(location_key PK, branch_id, business_id, branch_name, region, country)
dim_date(date_key PK, date, day, week, month, quarter, year, is_weekend)
```

### Facts

```
fact_sales(sale_key, date_key, product_key, customer_key, location_key,
           quantity, unit_price, unit_cost, revenue, gross_profit, discount, status)

fact_inventory(date_key, product_key, location_key,
               opening_stock, closing_stock, movements_in, movements_out,
               daily_demand, days_remaining, reorder_point, risk_flag)

fact_payments(payment_key, date_key, location_key, customer_key NULL,
              supplier_key NULL, direction, amount, currency, method)

fact_purchase_orders(po_key, date_key, product_key, supplier_key, location_key,
                     quantity, unit_cost, order_date, received_date,
                     lead_time_days, on_time_flag)
```

### Feature marts (feed ML + BI)

```
mart_daily_revenue(date, business_id, branch_id, revenue, orders, aov, gross_margin)
mart_product_demand_daily(date, product_id, branch_id, qty, rolling_7, rolling_30, dow, month)
mart_customer_rfm(customer_id, recency_days, frequency, monetary, r_score, f_score, m_score, segment)
mart_supplier_scorecard(supplier_id, orders, avg_delivery_days, on_time_pct,
                        avg_cost, reliability_score, risk_tier)
mart_cashflow_daily(date, business_id, inflow, outflow, net, closing_balance)
```

### Grain

- `fact_sales`: one row per sale line item.
- `fact_inventory`: one row per product × location × day.
- `fact_payments`: one row per payment.
- `fact_purchase_orders`: one row per PO line.

---

## 6. Airflow Architecture

| DAG | Schedule | Purpose |
|---|---|---|
| `ingest_sales` | `@hourly` | Pull POS/CSV sales into `raw_sales` landing schema |
| `ingest_inventory` | `@daily` | Pull stock movements into `raw_inventory` |
| `ingest_customers` | `@daily` | Pull customer + supplier master into `raw_customers`, `raw_suppliers` |
| `transform_data` | `@daily`, after ingests | Spark jobs: clean, dedupe, standardize currencies/dates → `curated_*` |
| `build_warehouse` | `@daily` | Trigger `dbt run` + `dbt test` → dims + facts + marts |
| `train_forecasting_models` | `@weekly` | Retrain demand + cashflow + segmentation, log to MLflow, promote champion |

Every DAG:

- `start → task(s) → validate → notify → end`
- Retries: 3× with 5-minute exponential backoff
- SLA per DAG; miss triggers alert task
- All tasks idempotent (partitioned by execution date)

---

## 7. dbt Architecture

**Project name:** `sme_intelligence`

### Layers

**Staging** (`models/staging/`) — 1:1 with source, light typing and renaming only.

- `stg_sales`, `stg_sale_items`
- `stg_inventory`, `stg_customers`, `stg_suppliers`, `stg_products`
- `stg_payments`, `stg_purchase_orders`

**Marts — dimensions** (`models/marts/dims/`)

- `dim_customer`, `dim_product`, `dim_supplier`, `dim_location`, `dim_date`

**Marts — facts** (`models/marts/facts/`)

- `fact_sales`, `fact_inventory`, `fact_payments`, `fact_purchase_orders`

**Marts — feature tables** (`models/marts/`)

- `mart_daily_revenue`, `mart_product_demand_daily`, `mart_customer_rfm`,
  `mart_supplier_scorecard`, `mart_cashflow_daily`

### Generic tests

- `not_null` on all surrogate and natural keys
- `unique` on surrogate keys and business keys
- `relationships` fact → dim on every FK
- `accepted_values` on `status`, `risk_flag`, `direction`, `segment`, `risk_tier`

### Singular tests (`tests/`)

- `assert_positive_quantity`
- `assert_no_negative_stock`
- `assert_revenue_matches_items`

---

## 8. ML Architecture

### Models

| Model | Task | Algorithm | Output |
|---|---|---|---|
| Demand Forecasting | product × location time series | XGBoost (lag features) + seasonal baseline | 7/14/30-day forecast + CI |
| Cash-Flow Forecasting | daily cash balance | XGBoost + Prophet baseline | 30-day projected balance + shortage date |
| Customer Segmentation | RFM clustering | KMeans (k=5) + rules fallback | segment label per customer |
| Supplier Reliability | scoring | Weighted score + Gradient Boost | reliability %, on-time %, risk tier |

### Feature store (fed by dbt marts)

- Lag windows: t-1, t-7, t-14, t-30
- Rolling mean/std: 7, 14, 30 days
- Seasonality: day-of-week, month, holiday flags
- Price/cost deltas
- RFM: recency, frequency, monetary
- Supplier lead-time variance

### Training flow

```
mart_* (dbt) → feature builder → train (XGBoost / KMeans / GB)
             → MLflow log (params, metrics, artifacts)
             → evaluate vs current champion
             → register model → promote if better
```

### Serving flow

```
FastAPI endpoint → ml_client → ml/serving.main
                             → loads champion from MLflow registry
                             → reads features from warehouse marts (5-min cache)
                             → returns forecast + CI + metrics
```

### Metrics tracked

- MAE, RMSE, MAPE (demand, cashflow)
- Silhouette (segmentation)
- R², on-time accuracy (supplier)
- Shadow evaluation window: 14 days before promotion

---

## 9. API Specification

Base path: `/api/v1`
Auth: `Authorization: Bearer <JWT>`
Common query params: `business_id`, `branch_id`, `currency` (`KES|USD`), `date_from`, `date_to`

### `GET /dashboard`

```json
{
  "kpis": {
    "revenue": 1840000,
    "gross_profit": 512000,
    "inventory_value": 940000,
    "outstanding_payments": 210000,
    "cash_balance": 320000,
    "currency": "KES"
  },
  "revenue_trend": [{ "date": "2025-08-01", "value": 52000 }],
  "cashflow_forecast": [
    { "date": "2025-09-01", "balance": 305000, "lower": 280000, "upper": 330000 }
  ],
  "inventory_risk": [
    { "product": "Tomato Seeds", "days_remaining": 9, "risk": "HIGH" }
  ],
  "recommendations": [{ "id": "rec-001", "type": "inventory", "title": "..." }]
}
```

### `GET /sales`

Query: `date_from, date_to, branch_id, product_id, customer_id, group_by`
Returns KPIs (revenue, orders, AOV, gross margin) plus series arrays for time, product, category, location, top/bottom products.

### `GET /inventory`

```json
{
  "items": [{
    "product": "Tomato Seeds",
    "current_stock": 420,
    "daily_demand": 42,
    "days_remaining": 10,
    "reorder_point": 200,
    "supplier": "Agro Supplies Ltd",
    "risk": "HIGH"
  }]
}
```

### `GET /customers`

Totals (total, active, repeat, avg value), segment breakdown, RFM scatter data.

### `GET /suppliers`

Per supplier: orders, avg_delivery_days, on_time_pct, avg_cost, reliability_score.

### `GET /forecast/demand`

Query: `product_id, location_id, horizon_days (7|14|30)`

```json
{
  "product": "Tomato Seeds",
  "location": "Nairobi CBD",
  "history": [{ "date": "2025-07-01", "value": 40 }],
  "forecast": [{ "date": "2025-09-01", "value": 46, "lower": 39, "upper": 53 }],
  "metrics": { "model": "xgboost", "mae": 3.4, "rmse": 5.1, "mape": 0.081 }
}
```

### `GET /forecast/cashflow`

Query: `horizon_days`
Returns current cash, expected income, expected expenses, daily projected balance with CI, shortage alerts list, recommendation text.

### `GET /recommendations`

```json
{
  "items": [{
    "id": "rec-001",
    "type": "inventory",
    "problem": "Inventory stockout risk.",
    "evidence": "Demand increased 24% over the last 30 days.",
    "recommendation": "Order 150 additional units.",
    "expected_impact": "Reduce stockout probability from 68% to 14%.",
    "priority": "high"
  }]
}
```

**Error shape (all endpoints):**

```json
{ "error": { "code": "...", "message": "...", "details": {} } }
```

---

## 10. UI Page Hierarchy & Routes

```
/                       → redirects to /dashboard
/dashboard              → Main intelligence dashboard
/sales                  → Sales analytics
/inventory              → Inventory intelligence
/forecast/demand        → Demand forecasting
/forecast/cashflow      → Cash flow intelligence
/customers              → Customer analytics + RFM segments
/suppliers              → Supplier scorecard
/recommendations        → AI recommendations hub
/settings               → Business, branches, currency, users
```

**Shared layout**

- Top header: business name · date range picker · branch selector · currency toggle (KES/USD) · notifications bell · user menu
- Left sidebar nav with icons
- Content area: responsive grid — KPI cards → charts → tables → recommendation cards

---

## 11. Design System

**Palette**

- Background: `#F7F8FA`; Cards: `#FFFFFF`
- Border: `1px solid #EAECEF`
- Radius: `14px`
- Primary (indigo): `#4F46E5`
- Success (healthy): `#16A34A`
- Warning (low): `#D97706`
- Error (critical): `#DC2626`
- Text: `#0F172A` primary, `#64748B` secondary

**Typography**

- Font: Inter / system UI
- KPI numerals: 32–40px, weight 600, tabular numerals
- Headings: 600 weight, tight letter-spacing

**Charts**

- Recharts or MUI X Charts
- Professional thin gridlines, muted axis text, one accent color per series

**Status pills**

- Healthy — green
- Low — amber
- Critical — red

**Recommendation cards**

- Type badge (Inventory / Cash Flow / Pricing / Customer / Supplier)
- Four sections: **Problem → Evidence → Recommendation → Expected Impact**
- Priority indicator (high / medium / low)

The app must feel like a premium enterprise analytics product, not an accounting spreadsheet.

---

## 12. Seed Data Contract

`backend/scripts/seed.py` populates `sme_oltp` with a reproducible Nairobi agro-supply dataset.

**Determinism:** `random.seed(42)` and `Faker.seed(42)`.

**Reference business:** GreenHarvest Agro Supplies, country Kenya, base currency KES.

**Branches (3):** Nairobi CBD (weight 1.00), Westlands (0.75), Thika Road (0.60).

**Products (55):** 6 categories — Seeds, Fertilizers, Pesticides, Farm Tools, Animal Feed, Irrigation. Each product has a real supplier, cost, sell price, reorder point, and lead time.

**Suppliers (18):** varying base lead times (3–7 days) and on-time rates (0.80–0.95).

**Customers (380):** distributed across 7 RFM archetypes with distinct active windows and purchase probabilities — guarantees KMeans produces 5 clean segments:

| Archetype | Share | Window | Daily prob | Basket |
|---|---|---|---|---|
| high_value | 5% | full | 0.55 | 1.6× |
| loyal | 15% | full | 0.22 | 1.2× |
| potential | 15% | last 150d | 0.12 | 1.0× |
| new | 20% | last 60d | 0.06 | 0.9× |
| at_risk | 15% | first half only | 0.20 | 1.1× |
| hibernating | 15% | first 3 months | 0.09 | 0.9× |
| lost | 15% | first ~1 month | 0.03 | 0.8× |

**Time window:** 2025-03-01 → 2025-09-30 (~7 months, 214 days).

**Behavioral features baked in**

- Weekend uplift (+30%), payday uplift (+35% on the 1st, 15th, 28th)
- Planting-season uplift (Mar–May, Sep–Oct)
- Recurring expenses: rent (1st), utilities + internet (5th), marketing (15th), salaries (28th)
- Weekly restock check on Mondays for products below reorder point
- ~78 % of sales paid immediately; the rest pending or cancelled

**Planted problem patterns (must be preserved):**

1. **Stockout risk** — `Tomato Seeds` (`TOM-SEED`): demand grows 1× → 3× over the window while reorders are deliberately cut to 35 %. Net stock trends toward zero across all branches.
2. **Degrading supplier** — `Rift Valley Agro Distributors`: lead time inflates by up to +3 days and on-time rate decays from 0.90 → ~0.55 over the last 120 days.
3. **Cash shortage** — three stress outflows in the last 45 days: bulk inventory prepayment (KES 1.2M), vehicle deposit (KES 1.5M), quarterly tax (KES 650K). Net cash flow turns negative; ending balance approaches the KES 150K minimum-safe threshold.

---

## 13. Localization & Multi-Tenancy

**Currencies:** KES (default) and USD. Every monetary column stores its own `currency`. Conversion happens in the presentation layer using a rates table (added in Slice 10). No silent currency mixing in aggregates.

**Dates:** stored `TIMESTAMPTZ`, displayed in the tenant's locale. East Africa (UTC+3) is the default display timezone for demo data.

**Multi-tenancy:** every business-scoped table carries `business_id`. API requires it as a filter. Row-level security is a future option (Slice 10), not a first-class requirement today.

**Branches:** all dashboards support branch filtering; the API accepts `branch_id` and defaults to "all branches for the business".

---

## 14. Development Roadmap

Every slice is a working vertical: schema → API → UI → tests → screenshot.

| # | Slice | Deliverable | Status |
|---|---|---|---|
| 0 | Foundation | Monorepo, docker-compose (frontend + backend + postgres), FastAPI `/health`, React landing page | ✅ done |
| 1a | OLTP + seed | Alembic migration `0001`, `scripts/seed.py`, 3 planted problem patterns | ✅ done |
| 1b | Dashboard slice | `/api/v1/dashboard` reading from OLTP view; MUI dashboard page with KPIs, revenue trend, inventory risk | ⏳ next |
| 2 | Sales Analytics | dbt staging + `fact_sales` + dims; `/sales` endpoint; Sales page with filters | — |
| 3 | Inventory Intelligence | `fact_inventory`, `mart_product_demand_daily`; `/inventory`; inventory table with risk | — |
| 4 | Customer Analytics | `mart_customer_rfm` + KMeans; `/customers`; segment visualization | — |
| 5 | Supplier Analytics | `mart_supplier_scorecard`; `/suppliers`; supplier scorecards | — |
| 6 | Demand Forecasting | XGBoost demand model, MLflow tracking, `/forecast/demand`; forecast page with CI | — |
| 7 | Cash-Flow Forecasting | Cash model + warehouse features; `/forecast/cashflow`; cash-flow page with shortage alerts | — |
| 8 | AI Recommendations | Rules + ML merged into `/recommendations`; recommendation hub | — |
| 9 | Data-Eng Hardening | Airflow DAGs, Spark jobs, dbt tests, SLAs | — |
| 10 | Polish & Ops | CI/CD, notifications, currency conversion, caching, docs | — |

---

## 15. Conventions

**Code**

- Python: 3.11, formatted with `ruff` + `black`, typed where it matters.
- TypeScript: strict mode on, no `any` in committed code.
- SQL: lowercase keywords, `snake_case` identifiers, one clause per line.
- Commit style: `slice-N: <short description>`.

**API**

- All endpoints under `/api/v1`.
- Pydantic v2 models for every request and response.
- All list endpoints return `{ "items": [...], "meta": {...} }` where pagination exists.
- No business logic in route handlers — routes call `services/`.

**Frontend**

- One folder per feature under `src/features/`.
- All API calls go through `src/api/`.
- Currency and date formatting live in `src/lib/`.
- No inline colors; everything pulls from `src/theme.ts`.

**Data**

- OLTP is write-optimized and indexed for point lookups.
- Warehouse is read-optimized and star-schema shaped.
- Every mart has at least one `not_null` and one `unique` test.

---

## 16. Definition of Done

A slice is done when **all** of the following are true:

1. Backend endpoint live with a typed Pydantic schema and matching tests.
2. Frontend page responsive, styled per §11, wired to the API — no mock data.
3. Data lineage documented: source table → mart → endpoint → UI component.
4. dbt tests pass (if the slice touches the warehouse).
5. Backend unit tests pass; frontend builds with zero TypeScript errors.
6. Screenshot + one-line demo note added to `README.md`.
7. `docker compose up --build` boots cleanly from a fresh clone.

---

*End of PROJECT_PLAN.md — treat this as the canonical reference for all subsequent work.*