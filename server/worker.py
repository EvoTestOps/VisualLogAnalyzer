import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL")

celery_app = Celery("worker", broker=broker_url, backend=broker_url)
