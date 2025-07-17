import dash
from dash_app.page_templates.datatable_result_page_base import (
    create_layout,
    register_callback,
)

config = {
    "title": "Distance File Level",
    "path_template": "/analysis/distance-file-level/<analysis_id>",
    "ids": {
        "project_link": "project-link-dis-file-res",
        "analysis_id": "analysis-id-dis-file-res",
        "datatable": "datatable-dis-file-res",
        "metadata": "metadata-dis-file-res",
        "error_toast": "error-toast-dis-file-res",
        "success_toast": "success-toast-dis-file-res",
    },
}

dash.register_page(__name__, path_template=config["path_template"])


def layout(analysis_id=None, **kwargs):
    return create_layout(config, analysis_id)


register_callback(config)
