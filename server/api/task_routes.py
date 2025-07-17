from celery.result import AsyncResult
from flask import Blueprint, jsonify

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)

    response = {
        "ready": task_result.ready(),
        "successful": task_result.successful(),
        "result": None,
        "state": task_result.state,
    }

    if task_result.ready():
        if task_result.state == "FAILURE":
            response["result"] = {"error": str(task_result.result)}

        else:
            response["result"] = task_result.result

    return jsonify(response)
