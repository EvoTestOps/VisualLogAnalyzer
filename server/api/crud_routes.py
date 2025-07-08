import io
import logging

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError
from sqlalchemy.inspection import inspect

from server.extensions import db
from server.models.analysis import Analysis
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


@crud_bp.route("/projects/<int:project_id>/analyses", methods=["GET"])
def get_analyses(project_id: int):
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"error": f"No project found with id: {project_id}"}), 404

    result = [analysis.to_dict() for analysis in project.analyses]
    return jsonify(result)


@crud_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return jsonify({"error": f"Analysis not found. Id: {analysis_id}"}), 404

    buffer = None
    try:
        with open(analysis.results_path, "rb") as file:
            buffer = io.BytesIO(file.read())

        buffer.seek(0)

        return Response(buffer.getvalue(), mimetype="application/octet-stream")
    except Exception as e:
        logging.error(
            f"Error fetching results for analysis {analysis_id}: {str(e)}",
            exc_info=True,
        )
        return jsonify({"error": str(e)}), 500
    finally:
        if buffer:
            buffer.close()


@crud_bp.route("/analyses/<int:analysis_id>/metadata", methods=["GET"])
def get_analysis_metadata(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return jsonify({"error": f"Analysis not found. Id: {analysis_id}"}), 404

    attributes = inspect(analysis).attrs

    metadata = {
        attr.key: getattr(analysis, attr.key)
        for attr in attributes
        if getattr(analysis, attr.key) is not None and attr.key != "project"
    }

    if "time_created" in metadata:
        metadata["time_created"] = analysis.time_created.isoformat()

    if "time_updated" in metadata:
        metadata["time_updated"] = analysis.time_updated.isoformat()

    return jsonify(metadata)
