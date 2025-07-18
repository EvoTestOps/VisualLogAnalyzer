import dash
from dash_app.page_templates.distance_create_page_base import (
    create_layout,
    register_callbacks,
)

config = {
    "type": "distance-directory-level",
    "level": "directory",
    "path_template": "/analysis/distance-directory-level/create",
    "base_ids": {
        "title": "New Directory Level Log Distance",
        "error_toast_id": "error-toast-dis-dir-new",
        "success_toast_id": "success-toast-dis-dir-new",
        "url_id": "url-dis-dir-new",
        "redirect_id": "analysis-id-dis-dir-new",
        "project_store_id": "project-store-dis-dir-new",
    },
    "form_input_ids": {
        "submit_id": "submit-dis-dir-new",
        "directory_id": "directory-dis-dir-new",
        "enhancement_id": "enhancement-dis-dir-new",
        "target_run_id": "target-dis-dir-new",
        "runs_filter_id": "filter-dis-dir-new",
        "mask_id": "mask-dis-dir-new",
        "vectorizer_id": "vectorizer-dis-dir-new",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(**kwargs):
    return create_layout(config)


register_callbacks(config)
