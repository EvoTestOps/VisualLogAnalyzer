from datetime import datetime, timezone
from celery.result import AsyncResult
from flask import Blueprint, jsonify

task_bp = Blueprint("tasks", __name__)


@task_bp.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)

    meta = task_result.info if isinstance(task_result.info, dict) else {}
    response = {
        "ready": task_result.ready(),
        "successful": task_result.successful(),
        "result": None,
        "state": task_result.state,
        "meta": meta,
    }

    if task_result.ready():
        if task_result.state == "FAILURE":
            response["result"] = {"error": str(task_result.result)}
        else:
            response["result"] = task_result.result.get("result")
            response["meta"] = task_result.result.get("meta", {})

    if response["meta"] and "start_time" in response["meta"]:
        start_time = datetime.fromisoformat(response["meta"]["start_time"])
        response["meta"]["relative_time"] = _get_relative_time(start_time)

    return jsonify(response)


def _get_relative_time(start_time):
    time_now = datetime.now(timezone.utc)
    delta = time_now - start_time

    if delta.total_seconds() < 60:
        return f"{int(delta.total_seconds())} seconds"
    else:
        return f"{int(delta.total_seconds() / 60)} minutes"
