from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from server.extensions import db
from server.models.project import Project

from .validator_models.crud_params import ProjectParams

crud_bp = Blueprint("crud", __name__)


@crud_bp.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])


@crud_bp.route("/projects", methods=["POST"])
def create_project():
    try:
        validated_data = ProjectParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]  # take the first one
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    project = Project(name=validated_data.name)
    db.session.add(project)
    db.session.commit()

    return jsonify({"id": project.id})


@crud_bp.route("/analyses/<int:project_id>", methods=["GET"])
def get_analyses(project_id: int):
    project = db.session.get(Project, project_id)
    result = [analysis.to_dict() for analysis in project.analyses]
    return jsonify(result)
