import gc
import traceback
from datetime import datetime, timezone

from celery import shared_task
from celery.exceptions import Ignore

from server.analysis.analysis_runners import (
    run_anomaly_detection_analysis,
    run_file_count_analysis,
    run_log_distance_analysis,
    run_umap_analysis,
    run_unique_terms_analysis,
)


@shared_task(bind=True, ignore_results=False)
def async_run_anomaly_detection(
    self,
    project_id: int,
    analysis_name: str | None,
    train_data_path: str,
    test_data_path: str,
    models: list[str],
    item_list_col: str,
    runs_to_include: list[str] | None,
    runs_to_include_train: list[str] | None,
    files_to_include: list[str] | None,
    files_to_include_train: list[str] | None,
    file_level: bool,
    directory_level: bool,
    mask_type: str,
    vectorizer: str,
) -> dict:
    start_time = datetime.now(timezone.utc).isoformat()
    meta = {"analysis_type": "Anomaly detection", "start_time": start_time}
    logs = []
    self.update_state(state="STARTED", meta=meta)

    try:
        result = run_anomaly_detection_analysis(
            project_id,
            analysis_name,
            train_data_path,
            test_data_path,
            models,
            item_list_col,
            runs_to_include,
            runs_to_include_train,
            files_to_include,
            files_to_include_train,
            file_level,
            directory_level,
            mask_type,
            vectorizer,
            log=_make_logger(self, meta, logs),
        )

        completed_time = datetime.now(timezone.utc).isoformat()
        meta["completed_time"] = completed_time

        return {
            "result": result,
            "meta": {**meta, "logs": logs},
        }
    except Exception as exc:
        completed_time = datetime.now(timezone.utc).isoformat()
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": traceback.format_exc().split("\n"),
                "meta": {**meta, "completed_time": completed_time},
                "error_msg": str(exc),
            },
        )
        raise Ignore()
    finally:
        gc.collect()


@shared_task(bind=True, ignore_results=False)
def async_run_file_counts(
    self, project_id: int, analysis_name: str | None, directory_path: str
) -> dict:
    start_time = datetime.now(timezone.utc).isoformat()
    meta = {"analysis_type": "File counts", "start_time": start_time}
    logs = []

    self.update_state(state="STARTED", meta=meta)

    try:
        result = run_file_count_analysis(
            project_id,
            analysis_name,
            directory_path,
            log=_make_logger(self, meta, logs),
        )

        completed_time = datetime.now(timezone.utc).isoformat()
        meta["completed_time"] = completed_time

        return {
            "result": result,
            "meta": {**meta, "logs": logs},
        }
    except Exception as exc:
        completed_time = datetime.now(timezone.utc).isoformat()
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": traceback.format_exc().split("\n"),
                "meta": {**meta, "completed_time": completed_time},
                "error_msg": str(exc),
            },
        )
        raise Ignore()
    finally:
        gc.collect()


@shared_task(bind=True, ignore_results=False)
def async_run_unique_terms(
    self,
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    mask_type: str,
) -> dict:
    start_time = datetime.now(timezone.utc).isoformat()
    meta = {"analysis_type": "Unique terms", "start_time": start_time}
    logs = []

    self.update_state(state="STARTED", meta=meta)

    try:
        result = run_unique_terms_analysis(
            project_id,
            analysis_name,
            directory_path,
            item_list_col,
            file_level,
            mask_type,
            log=_make_logger(self, meta, logs),
        )

        completed_time = datetime.now(timezone.utc).isoformat()
        meta["completed_time"] = completed_time

        return {
            "result": result,
            "meta": {**meta, "logs": logs},
        }
    except Exception as exc:
        completed_time = datetime.now(timezone.utc).isoformat()
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": traceback.format_exc().split("\n"),
                "meta": {**meta, "completed_time": completed_time},
                "error_msg": str(exc),
            },
        )
        raise Ignore()
    finally:
        gc.collect()


@shared_task(bind=True, ignore_results=False)
def async_create_umap(
    self,
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    item_list_col: str,
    file_level: bool,
    vectorizer: str,
    mask_type: str,
) -> dict:
    start_time = datetime.now(timezone.utc).isoformat()
    meta = {"analysis_type": "UMAP", "start_time": start_time}
    logs = []

    self.update_state(state="STARTED", meta=meta)

    try:
        result = run_umap_analysis(
            project_id,
            analysis_name,
            directory_path,
            item_list_col,
            file_level,
            vectorizer,
            mask_type,
            log=_make_logger(self, meta, logs),
        )

        completed_time = datetime.now(timezone.utc).isoformat()
        meta["completed_time"] = completed_time

        return {
            "result": result,
            "meta": {**meta, "logs": logs},
        }
    except Exception as exc:
        completed_time = datetime.now(timezone.utc).isoformat()
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": traceback.format_exc().split("\n"),
                "meta": {**meta, "completed_time": completed_time},
                "error_msg": str(exc),
            },
        )
        raise Ignore()
    finally:
        gc.collect()


@shared_task(bind=True, ignore_results=False)
def async_log_distance(
    self,
    project_id: int,
    analysis_name: str | None,
    directory_path: str,
    target_run: str,
    comparison_runs: list[str] | None,
    item_list_col: str,
    file_level: bool,
    mask_type: str | None,
    vectorizer: str,
) -> dict:
    start_time = datetime.now(timezone.utc).isoformat()
    meta = {"analysis_type": "Log distance", "start_time": start_time}
    logs = []

    self.update_state(state="STARTED", meta=meta)

    try:
        result = run_log_distance_analysis(
            project_id,
            analysis_name,
            directory_path,
            target_run,
            comparison_runs,
            item_list_col,
            file_level,
            mask_type,
            vectorizer,
            log=_make_logger(self, meta, logs),
        )

        completed_time = datetime.now(timezone.utc).isoformat()
        meta["completed_time"] = completed_time

        return {
            "result": result,
            "meta": {**meta, "logs": logs},
        }
    except Exception as exc:
        completed_time = datetime.now(timezone.utc).isoformat()
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(exc).__name__,
                "exc_message": traceback.format_exc().split("\n"),
                "meta": {**meta, "completed_time": completed_time},
                "error_msg": str(exc),
            },
        )
        raise Ignore()
    finally:
        gc.collect()


def _make_logger(self, meta, logs):
    def log_status(msg: str):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": msg,
        }
        logs.append(log_entry)
        self.update_state(state="PROGRESS", meta={**meta, "logs": logs})

    return log_status
