from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    customers,
    dashboard,
    forecast_cashflow,
    forecast_demand,
    inventory,
    meta,
    recommendations,
    sales,
    suppliers,
)
from app.core.config import settings

app = FastAPI(title=settings.api_title, version=settings.api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {
        "status": "ok",
        "service": "backend",
        "env": settings.api_env,
        "version": settings.api_version,
    }


app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(forecast_demand.router, prefix="/api/v1")
app.include_router(forecast_cashflow.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(meta.router, prefix="/api/v1")