from typing import Optional

from pydantic import BaseModel


class BranchOption(BaseModel):
    id: str
    name: str


class ProductOption(BaseModel):
    id: str
    name: str
    sku: str
    category: Optional[str] = None


class CustomerOption(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None