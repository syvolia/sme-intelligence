from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meta import BranchOption, CustomerOption, ProductOption

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/branches", response_model=list[BranchOption])
def list_branches(db: Session = Depends(get_db)) -> list[BranchOption]:
    rows = db.execute(
        text("SELECT id::text AS id, name FROM branches ORDER BY name")
    ).mappings().all()
    return [BranchOption(id=r["id"], name=r["name"]) for r in rows]


@router.get("/products", response_model=list[ProductOption])
def list_products(db: Session = Depends(get_db)) -> list[ProductOption]:
    rows = db.execute(
        text(
            """
            SELECT id::text AS id, name, sku, category
            FROM products
            ORDER BY category NULLS LAST, name
            """
        )
    ).mappings().all()
    return [
        ProductOption(
            id=r["id"], name=r["name"], sku=r["sku"], category=r["category"]
        )
        for r in rows
    ]


@router.get("/customers", response_model=list[CustomerOption])
def list_customers(
    q: Optional[str] = Query(None, description="Search by name (ILIKE)"),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[CustomerOption]:
    params: dict = {"limit": limit}
    where = ""
    if q:
        where = "WHERE name ILIKE :q"
        params["q"] = f"%{q}%"

    rows = db.execute(
        text(
            f"""
            SELECT id::text AS id, COALESCE(name,'') AS name, phone
            FROM customers
            {where}
            ORDER BY name NULLS LAST
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()

    return [
        CustomerOption(id=r["id"], name=r["name"], phone=r["phone"]) for r in rows
    ]