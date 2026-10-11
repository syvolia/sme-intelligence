.PHONY: help up down reset logs health \
        spark dbt dbt-curated warehouse pipeline \
        use-warehouse use-oltp \
        airflow-up airflow-down airflow-logs \
        seed migrate

help:
	@echo "Targets:"
	@echo "  up / down / reset / logs     — Docker Compose lifecycle"
	@echo "  health                        — verify all services"
	@echo "  migrate                       — run Alembic migrations"
	@echo "  seed                          — seed OLTP with realistic data"
	@echo "  spark                         — run the Spark cleaning job"
	@echo "  dbt / dbt-curated             — run dbt against public / curated"
	@echo "  warehouse                     — spark + dbt-curated (full build)"
	@echo "  pipeline                      — migrate + warehouse"
	@echo "  use-warehouse / use-oltp      — flip the backend read path"
	@echo "  airflow-up / airflow-down     — start/stop Airflow stack"

# ---------------------------------------------------------------------------
# Core lifecycle
# ---------------------------------------------------------------------------
up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v

logs:
	docker compose logs -f

health:
	@echo "--- backend ---"
	@curl -sS http://127.0.0.1:8001/health || echo "backend unreachable"
	@echo ""
	@echo "--- postgres ---"
	@docker compose exec -T postgres pg_isready -U sme -d sme_oltp

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m scripts.seed

# ---------------------------------------------------------------------------
# Data engineering
# ---------------------------------------------------------------------------
spark:
	docker compose run --rm --profile data spark \
	  /opt/spark/bin/spark-submit \
	    --master 'local[*]' \
	    --jars /opt/spark/jars/postgresql-42.7.3.jar \
	    /opt/spark/work-dir/jobs/clean_all.py

dbt:
	docker compose run --rm --profile data dbt \
	  bash -c "cd /dbt && dbt deps && \
	           dbt run  --profiles-dir /dbt && \
	           dbt test --profiles-dir /dbt"

dbt-curated:
	docker compose run --rm --profile data dbt \
	  bash -c "cd /dbt && dbt deps && \
	           dbt run  --vars '{source_schema: curated}' --profiles-dir /dbt && \
	           dbt test --vars '{source_schema: curated}' --profiles-dir /dbt"

warehouse: spark dbt-curated
	@echo ""
	@echo "✅ Warehouse built. Tables live in schema: analytics"

pipeline: migrate warehouse
	@echo ""
	@echo "✅ Full pipeline complete."

# ---------------------------------------------------------------------------
# Read-path switching
# ---------------------------------------------------------------------------
use-warehouse:
	@if ! grep -q "^WAREHOUSE_ENABLED=true" .env; then \
	  if grep -q "^WAREHOUSE_ENABLED=" .env; then \
	    sed -i.bak 's/^WAREHOUSE_ENABLED=.*/WAREHOUSE_ENABLED=true/' .env; \
	  else \
	    echo "WAREHOUSE_ENABLED=true" >> .env; \
	  fi; \
	fi
	@docker compose up -d backend
	@echo "✅ Backend now reads from analytics.* (warehouse mode)"

use-oltp:
	@if ! grep -q "^WAREHOUSE_ENABLED=false" .env; then \
	  if grep -q "^WAREHOUSE_ENABLED=" .env; then \
	    sed -i.bak 's/^WAREHOUSE_ENABLED=.*/WAREHOUSE_ENABLED=false/' .env; \
	  else \
	    echo "WAREHOUSE_ENABLED=false" >> .env; \
	  fi; \
	fi
	@docker compose up -d backend
	@echo "✅ Backend now reads from public.* (OLTP mode)"

# ---------------------------------------------------------------------------
# Airflow
# ---------------------------------------------------------------------------
airflow-up:
	docker compose --profile airflow up -d airflow-init airflow-webserver airflow-scheduler
	@echo ""
	@echo "Airflow UI: http://127.0.0.1:8080  (admin / admin)"

airflow-down:
	docker compose --profile airflow down

airflow-logs:
	docker compose --profile airflow logs -f airflow-scheduler