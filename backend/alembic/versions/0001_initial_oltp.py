"""Initial OLTP schema — businesses, branches, users, customers, suppliers,
products, sales, sale_items, inventory_movements, purchase_orders, payments,
cash_accounts.

Revision ID: 0001_initial_oltp
Revises:
Create Date: 2025-09-30
"""
from alembic import op

revision = "0001_initial_oltp"
down_revision = None
branch_labels = None
depends_on = None


DDL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- Tenancy & org
-- ---------------------------------------------------------------------------
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    country TEXT,
    base_currency TEXT NOT NULL DEFAULT 'KES',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_branches_business ON branches(business_id);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('owner','manager','analyst')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_business ON users(business_id);

-- ---------------------------------------------------------------------------
-- Master data
-- ---------------------------------------------------------------------------
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    contact TEXT,
    country TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_suppliers_business ON suppliers(business_id);

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT,
    phone TEXT,
    email TEXT,
    segment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_customers_business ON customers(business_id);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    unit TEXT,
    cost_price NUMERIC(14,2),
    sell_price NUMERIC(14,2),
    reorder_point INT NOT NULL DEFAULT 0,
    lead_time_days INT NOT NULL DEFAULT 3,
    supplier_id UUID REFERENCES suppliers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (business_id, sku)
);
CREATE INDEX idx_products_business ON products(business_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_category ON products(category);

-- ---------------------------------------------------------------------------
-- Transactions
-- ---------------------------------------------------------------------------
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id),
    customer_id UUID REFERENCES customers(id),
    sale_date TIMESTAMPTZ NOT NULL,
    currency TEXT NOT NULL,
    total_amount NUMERIC(14,2) NOT NULL,
    discount NUMERIC(14,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL CHECK (status IN ('paid','pending','cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_sales_business_date ON sales(business_id, sale_date);
CREATE INDEX idx_sales_branch_date   ON sales(branch_id, sale_date);
CREATE INDEX idx_sales_customer      ON sales(customer_id);
CREATE INDEX idx_sales_status        ON sales(status);

CREATE TABLE sale_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL,
    unit_cost NUMERIC(14,2) NOT NULL
);
CREATE INDEX idx_sale_items_sale    ON sale_items(sale_id);
CREATE INDEX idx_sale_items_product ON sale_items(product_id);

CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id),
    product_id UUID NOT NULL REFERENCES products(id),
    movement_type TEXT NOT NULL CHECK (movement_type IN ('in','out','adjust')),
    quantity INT NOT NULL,
    movement_date TIMESTAMPTZ NOT NULL,
    reference TEXT
);
CREATE INDEX idx_inv_mov_business_date   ON inventory_movements(business_id, movement_date);
CREATE INDEX idx_inv_mov_branch_product  ON inventory_movements(branch_id, product_id);

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_cost NUMERIC(14,2) NOT NULL,
    order_date TIMESTAMPTZ NOT NULL,
    expected_date TIMESTAMPTZ,
    received_date TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('open','received','cancelled'))
);
CREATE INDEX idx_po_business_date ON purchase_orders(business_id, order_date);
CREATE INDEX idx_po_supplier      ON purchase_orders(supplier_id);
CREATE INDEX idx_po_product       ON purchase_orders(product_id);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    sale_id UUID REFERENCES sales(id),
    purchase_order_id UUID REFERENCES purchase_orders(id),
    direction TEXT NOT NULL CHECK (direction IN ('in','out')),
    amount NUMERIC(14,2) NOT NULL,
    currency TEXT NOT NULL,
    payment_date TIMESTAMPTZ NOT NULL,
    method TEXT
);
CREATE INDEX idx_payments_business_date ON payments(business_id, payment_date);
CREATE INDEX idx_payments_direction     ON payments(direction);

CREATE TABLE cash_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id),
    balance NUMERIC(14,2) NOT NULL,
    currency TEXT NOT NULL,
    min_safe_balance NUMERIC(14,2) NOT NULL DEFAULT 150000,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cash_business_branch ON cash_accounts(business_id, branch_id);
"""


DROP = """
DROP TABLE IF EXISTS cash_accounts CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS inventory_movements CASCADE;
DROP TABLE IF EXISTS sale_items CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS businesses CASCADE;
"""


def upgrade() -> None:
    op.execute(DDL)


def downgrade() -> None:
    op.execute(DROP)