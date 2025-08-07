from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from server.api.validator_models.anomaly_detection_params import AnomalyDetectionParams
from server.api.validator_models.high_level_analysis_params import (
    FileCountsParams,
    UmapParams,
    UniqueTermsParams,
)
from server.api.validator_models.log_distance_params import LogDistanceParams
from server.tasks import (
    async_create_umap,
    async_log_distance,
    async_run_anomaly_detection,
    async_run_file_counts,
    async_run_unique_terms,
)

analyze_bp = Blueprint("main", __name__)


def validate_request_data(params_model, request):
    try:
        validated_data = params_model(**request.get_json())
        return validated_data
    except ValidationError as e:
        error = e.errors()[0]
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400


@analyze_bp.route("/manual-test-train/<int:project_id>", methods=["POST"])
def manual_test_train(project_id):
    validation_result = validate_request_data(AnomalyDetectionParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    train_data_path = validation_result.train_data_path
    test_data_path = validation_result.test_data_path
    models = validation_result.models
    item_list_col = validation_result.item_list_col
    runs_to_include = validation_result.runs_to_include
    files_to_include = validation_result.files_to_include
    file_level = validation_result.file_level
    run_level = validation_result.run_level
    mask_type = validation_result.mask_type
    vectorizer = validation_result.vectorizer

    task = async_run_anomaly_detection.delay(
        project_id,
        train_data_path,
        test_data_path,
        models,
        item_list_col,
        runs_to_include,
        files_to_include,
        file_level,
        run_level,
        mask_type,
        vectorizer,
    )

    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/unique-terms/<int:project_id>", methods=["POST"])
def run_unique_terms(project_id: int):
    validation_result = validate_request_data(UniqueTermsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level

    task = async_run_unique_terms.delay(project_id, dir_path, item_list_col, file_level)

    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/umap/<int:project_id>", methods=["POST"])
def create_umap(project_id):
    validation_result = validate_request_data(UmapParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level
    vectorizer = validation_result.vectorizer
    mask_type = validation_result.mask_type

    task = async_create_umap.delay(
        project_id, dir_path, item_list_col, file_level, vectorizer, mask_type
    )

    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/file-counts/<int:project_id>", methods=["POST"])
def run_file_counts(project_id: int):
    validation_result = validate_request_data(FileCountsParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    analysis_name = validation_result.name

    task = async_run_file_counts.delay(project_id, analysis_name, dir_path)
    return jsonify({"task_id": task.id}), 202


@analyze_bp.route("/log-distance/<int:project_id>", methods=["POST"])
def log_distance(project_id):
    validation_result = validate_request_data(LogDistanceParams, request)
    if isinstance(validation_result, tuple):
        return validation_result

    dir_path = validation_result.directory_path
    target_run = validation_result.target_run
    comparison_runs = validation_result.comparison_runs
    item_list_col = validation_result.item_list_col
    file_level = validation_result.file_level
    mask_type = validation_result.mask_type
    vectorizer = validation_result.vectorizer

    task = async_log_distance.delay(
        project_id,
        dir_path,
        target_run,
        comparison_runs,
        item_list_col,
        file_level,
        mask_type,
        vectorizer,
    )
    return jsonify({"task_id": task.id}), 202
