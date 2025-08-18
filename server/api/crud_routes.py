import os
import io
import logging

import polars as pl
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

    project = Project(name=validated_data.name, base_path=validated_data.base_path)
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


@crud_bp.route("/projects/<int:project_id>/base_path", methods=["GET"])
def get_project_base_path(project_id: int):
    project = db.get_or_404(Project, project_id)
    return jsonify({"base_path": project.base_path}), 200


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
    settings.line_level_display_mode = validated_data.line_level_display_mode
    settings.manual_filename_input = validated_data.manual_filename_input
    db.session.commit()

    return {}, 200


@crud_bp.route("/projects/<int:project_id>/settings", methods=["GET"])
def get_settings(project_id: int):
    settings = Settings.query.filter_by(project_id=project_id).first_or_404()

    return jsonify(settings.to_dict()), 200


@crud_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id: int):
    raw = request.args.get("raw", "false").lower() == "true"
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return jsonify({"error": f"Analysis not found. Id: {analysis_id}"}), 404

    buffer = None
    try:
        with open(analysis.results_path, "rb") as file:
            buffer = io.BytesIO(file.read())

        buffer.seek(0)

        if analysis.analysis_level == "line" and not raw:
            settings = Settings.query.filter_by(
                project_id=analysis.project_id
            ).first_or_404()
            display_mode = settings.line_level_display_mode

            if display_mode == "data_points_only":
                df = pl.read_parquet(buffer)
                columns_to_drop = [col for col in df.columns if "moving_avg" in col]
            elif display_mode == "moving_avg_only":
                df = pl.read_parquet(buffer)
                columns_to_drop = [
                    col
                    for col in df.columns
                    if "pred_ano_proba" in col and not col.startswith("moving_avg")
                ]
            else:
                return Response(buffer.getvalue(), mimetype="application/octet-stream")

            if columns_to_drop:
                df = df.drop([col for col in columns_to_drop if col in df.columns])
                buffer = io.BytesIO()
                df.write_parquet(buffer)
                buffer.seek(0)
            else:
                buffer.seek(0)
                return Response(buffer.getvalue(), mimetype="application/octet-stream")

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


@crud_bp.route("/analyses/<int:analysis_id>/name", methods=["PATCH"])
def update_analysis_name(analysis_id: int):
    analysis = Analysis.query.filter_by(id=analysis_id).first_or_404()

    name = request.get_json().get("name")
    if not name:
        return {"error": "Name is required"}, 400

    analysis.name = name
    db.session.commit()

    return {}, 200
