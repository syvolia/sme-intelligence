"""Create curated and analytics schemas.

Revision ID: 0002_warehouse_schemas
Revises: 0001_initial_oltp
Create Date: 2025-09-25
"""
from alembic import op

revision = "0002_warehouse_schemas"
down_revision = "0001_initial_oltp"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS curated")
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
    op.execute("DROP SCHEMA IF EXISTS curated CASCADE")