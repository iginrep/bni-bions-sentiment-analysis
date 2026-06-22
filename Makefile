PY=python3
COMPOSE?=docker-compose

.PHONY: test collect backfill sentiment-backfill analyze export api mongo-up mongo-down mongo-logs mongo-shell mongo-status

test:
	$(PY) -m pytest -q

collect:
	$(PY) -m pipeline.collector.run

backfill:
	$(PY) -m pipeline.collector.backfill

sentiment-backfill:
	$(PY) -c "from dotenv import load_dotenv; load_dotenv(); from pipeline.sentiment.run import backfill_sentiment; print(f'backfilled {backfill_sentiment()} items')"

analyze:
	$(PY) -m pipeline.sentiment.run

export:
	$(PY) -m pipeline.export.csv_export

api:
	$(PY) -m uvicorn apps.api.app.main:app --reload

mongo-up:
	$(COMPOSE) up -d mongo

mongo-down:
	$(COMPOSE) down

mongo-logs:
	$(COMPOSE) logs --tail=100 -f mongo

mongo-shell:
	$(COMPOSE) exec mongo mongosh bni_bions_sentiment

mongo-status:
	$(COMPOSE) ps
