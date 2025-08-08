from flask import Flask
from flask_migrate import Migrate

from dash_app import create_dash_app
from server.config import Config
from server.extensions import db, celery_init_app

from server.models import settings, analysis, project
from server.api.dash_redirects import dash_redirects_bp
from server.api.analyze_routes import analyze_bp
from server.api.task_routes import task_bp
from server.api.crud_routes import crud_bp


def create_app():
    server = Flask(__name__)
    server.config.from_object(Config)

    db.init_app(server)

    migrate = Migrate(server, db)

    server.register_blueprint(analyze_bp, url_prefix="/api")
    server.register_blueprint(crud_bp, url_prefix="/api")
    server.register_blueprint(task_bp, url_prefix="/api")
    server.register_blueprint(dash_redirects_bp)

    create_dash_app(server)

    # with server.app_context():
    #     db.create_all()

    celery_init_app(server)
    return server
