import dash
from dash_app.page_templates.distance_create_page_base import (
    create_layout,
    register_callbacks,
)

config = {
    "type": "distance-file-level",
    "level": "file",
    "path_template": "/analysis/distance-file-level/create",
    "base_ids": {
        "title": "New File Level Log Distance",
        "error_toast_id": "error-toast-dis-file-new",
        "success_toast_id": "success-toast-dis-file-new",
        "url_id": "url-dis-file-new",
        "redirect_id": "analysis-id-dis-file-new",
        "project_store_id": "project-store-dis-file-new",
    },
    "form_input_ids": {
        "submit_id": "submit-dis-file-new",
        "directory_id": "directory-dis-file-new",
        "enhancement_id": "enhancement-dis-file-new",
        "target_run_id": "target-dis-file-new",
        "runs_filter_id": "filter-dis-file-new",
        "mask_id": "mask-dis-file-new",
        "vectorizer_id": "vectorizer-dis-file-new",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config)
