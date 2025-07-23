from main import create_app
from server import tasks

server = create_app()
celery_app = server.extensions["celery"]

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
)
