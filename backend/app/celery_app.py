from celery import Celery
from .config import settings

broker_url = settings.celery_broker_url or settings.redis_url
backend_url = settings.celery_result_backend or settings.redis_url

app = Celery("marketai", broker=broker_url, backend=backend_url, include=["app.tasks"])
app.conf.beat_schedule = {
    "ingest-prices": {"task": "app.tasks.ingest_prices", "schedule": 60.0},
    "ingest-news": {"task": "app.tasks.ingest_news", "schedule": 300.0},
    "update-signals": {"task": "app.tasks.update_signals", "schedule": 60.0},
}
app.conf.timezone = "UTC"
