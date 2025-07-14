from main import create_app
from server import tasks

server = create_app()
celery_app = server.extensions["celery"]
