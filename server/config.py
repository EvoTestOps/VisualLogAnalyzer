import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESULTS_PATH = os.getenv("RESULTS_DIRECTORY")
    LOG_DATA_PATH = os.getenv("LOG_DATA_DIRECTORY")
    # CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY = {
        "broker_url": os.getenv("CELERY_BROKER_URL"),
        "result_backend": os.getenv("CELERY_BROKER_URL"),
    }
