import dash
from dash_app.page_templates.distance_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "Distance Directory Level",
    "path_template": "/analysis/distance-directory-level/<analysis_id>",
    "ids": {
        "project_link": "project-link-dis-dir-res",
        "analysis_id": "analysis-id-dis-dir-res",
        "datatable": "datatable-dis-dir-res",
        "metadata": "metadata-dis-dir-res",
        "error_toast": "error-toast-dis-dir-res",
        "success_toast": "success-toast-dis-dir-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)
