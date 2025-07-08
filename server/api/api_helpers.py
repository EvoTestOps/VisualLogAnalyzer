import logging

from flask import jsonify
from pydantic import ValidationError

from server.analysis.loader import Loader
from server.services.analysis_service import add_result


def validate_request_data(params_model, request):
    try:
        validated_data = params_model(**request.get_json())
        return validated_data
    except ValidationError as e:
        error = e.errors()[0]  # take the first one
        return jsonify({"error": f"{error['loc'][0]}: {error['msg']}"}), 400


def load_data(directory_path):
    loader = Loader(directory_path, "raw")
    loader.load()
    return loader.df


def store_and_format_result(result, project_id, analysis_type, metadata):
    result_id = add_result(result, project_id, analysis_type, **metadata)
    return jsonify({"id": result_id, "type": analysis_type})


def handle_errors(project_id, context, error):
    logging.error(
        f"Error processing {context} for project {project_id}: {str(error)}",
        exc_info=True,
    )
    return jsonify({"error": str(error)}), 500
