import dash
from dash_app.page_templates.new_analysis_page_base import (
    create_layout,
    register_callbacks,
)
from dash_app.callbacks.callback_functions import (
    run_anomaly_detection,
    fetch_project_settings,
)

config = {
    "type": "ano-file-level",
    "level": "file",
    "path_template": "/analysis/ano-file-level/create",
    "base_ids": {
        "title": "New File Level Anomaly Detection",
        "error_toast_id": "error-toast-ano-file-new",
        "success_toast_id": "success-toast-ano-file-new",
        "url_id": "url-ano-file-new",
        "redirect_id": "analysis-id-ano-file-new",
        "project_store_id": "project-store-ano-file-new",
        "interval_id": "interval-ano-file-new",
        "task_store_id": "task-store-ano-file-new",
        "project_link_id": "project-link-ano-file-new",
        "manual_filenames_id": "manual-filenames-ano-file-new",
    },
    "form_input_ids": {
        "submit_id": "submit-ano-file-new",
        "train_data_id": "train-data-ano-file-new",
        "test_data_id": "test-data-ano-file-new",
        "detectors_id": "detectors-ano-file-new",
        "enhancement_id": "enhancement-ano-file-new",
        "runs_filter_id": "filter-ano-file-new",
        "mask_input_id": "mask-ano-file-new",
        "vectorizer_id": "vectorizer-ano-file-new",
        "results_redirect_id": "results-redirect-ano-file-new",
        "analysis_name_id": "analysis-name-ano-file-new",
    },
    "input_fields": [
        "train_data_id",
        "test_data_id",
        "detectors_id",
        "enhancement_id",
        "runs_filter_id",
        "mask_input_id",
        "vectorizer_id",
        "results_redirect_id",
        "analysis_name_id",
    ],
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    project_id = kwargs.get("project_id")

    manual_filenames = False
    if project_id:
        settings = fetch_project_settings(project_id)
        manual_filenames = settings.get("manual_filename_input", False)

    config["manual_filenames"] = manual_filenames

    return create_layout(config)


register_callbacks(config, run_func=run_anomaly_detection)
