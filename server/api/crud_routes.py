import os
import io
import logging

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from server.extensions import db
from server.models.analysis import Analysis
from server.models.project import Project
from server.models.settings import Settings

from .validator_models.crud_params import ProjectParams, SettingsParams

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

    return jsonify({"id": project.id}), 201


@crud_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id: int):
    project = Project.query.filter_by(id=project_id).first_or_404()
    analyses = project.analyses

    try:
        for analysis in analyses:
            os.remove(analysis.results_path)

        db.session.delete(project)
        db.session.commit()
        return {}, 204

    except FileNotFoundError as e:
        logging.error(
            f"Error deleting project {project.name}, some of the results might not have been deleted or don't exist: {str(e)}",
            exc_info=True,
        )
        return jsonify({"error": str(e)}), 500


@crud_bp.route("/projects/<int:project_id>/name", methods=["GET"])
def get_project_name(project_id: int):
    project = db.get_or_404(Project, project_id)
    return jsonify({"name": project.name}), 200


@crud_bp.route("/projects/<int:project_id>/analyses", methods=["GET"])
def get_analyses(project_id: int):
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"error": f"No project found with id: {project_id}"}), 404

    result = [analysis.to_dict() for analysis in project.analyses]
    return jsonify(result)


@crud_bp.route("/projects/<int:project_id>/settings", methods=["PATCH"])
def update_settings(project_id: int):
    settings = Settings.query.filter_by(project_id=project_id).first_or_404()
    try:
        validated_data = SettingsParams(**request.get_json())
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400

    settings.match_filenames = validated_data.match_filenames
    settings.color_by_directory = validated_data.color_by_directory
    db.session.commit()

    return {}, 200


@crud_bp.route("/projects/<int:project_id>/settings", methods=["GET"])
def get_settings(project_id: int):
    settings = Settings.query.filter_by(project_id=project_id).first_or_404()

    return jsonify(settings.to_dict()), 200


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


@crud_bp.route("/analyses/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id: int):
    analysis = Analysis.query.filter_by(id=analysis_id).first_or_404()
    try:
        os.remove(analysis.results_path)
        db.session.delete(analysis)
        db.session.commit()
        return {}, 204

    except FileNotFoundError as e:
        logging.error(
            f"Error deleting analysis {analysis_id}, the results file might not exist: {str(e)}",
            exc_info=True,
        )
        return jsonify({"error": str(e)}), 500


@crud_bp.route("/analyses/<int:analysis_id>/metadata", methods=["GET"])
def get_analysis_metadata(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return jsonify({"error": f"Analysis not found. Id: {analysis_id}"}), 404

    metadata = {key: val for (key, val) in analysis.to_dict().items() if val}
    metadata["project_name"] = analysis.project.name

    return jsonify(metadata), 200
