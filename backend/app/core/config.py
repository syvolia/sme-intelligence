from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API metadata
    api_env: str = "development"
    api_title: str = "SME Intelligence API"
    api_version: str = "0.1.0"

    # Databases
    database_url: str = "postgresql://sme:sme@postgres:5432/sme_oltp"

    # MLflow
    mlflow_tracking_uri: str = "http://mlflow:5000"
    mlflow_demand_model_name: str = "demand_forecast_xgboost"
    mlflow_champion_alias: str = "champion"

    # Data warehouse — flip to true to read from analytics.* instead of public.*
    warehouse_enabled: bool = False
    warehouse_schema: str = "analytics"


settings = Settings()