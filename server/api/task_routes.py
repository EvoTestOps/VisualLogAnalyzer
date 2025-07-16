from celery.result import AsyncResult
from flask import Blueprint, jsonify

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)

    return jsonify(
        {
            "ready": task_result.ready(),
            "successful": task_result.successful(),
            "result": task_result.result if task_result.ready() else None,
        }
    )
