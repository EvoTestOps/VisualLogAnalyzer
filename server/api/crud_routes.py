from flask import Blueprint, request, jsonify
from server.extensions import db
from server.models.project import Project

crud_bp = Blueprint("crud", __name__)


@crud_bp.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])


@crud_bp.route("/projects", methods=["POST"])
def create_project():
    params = request.get_json()
    project = Project(name=params["name"])
    db.session.add(project)
    db.session.commit()
    return jsonify({"id": project.id})
