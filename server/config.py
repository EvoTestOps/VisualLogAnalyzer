import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESULTS_PATH = os.getenv("RESULTS_DIRECTORY")
    LOG_DATA_PATH = os.getenv("LOG_DATA_DIRECTORY")
