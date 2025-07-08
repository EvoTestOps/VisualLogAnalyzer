import dash
from dash import Input, Output, callback, html
from dash_app.components.layouts import (
    create_datatable_layout,
    create_result_base_layout,
)
from dash_app.callbacks.callback_functions import (
    populate_datatable,
)

dash.register_page(
    __name__,
    path_template="/analysis/ano-file-level/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    base = create_result_base_layout(
        "Anomaly Detection File Level",
        analysis_id,
        "project-link-ano-file-res",
        "analysis-id-ano-file-res",
    )
    content = create_datatable_layout(
        "datatable-ano-file-res",
        "metadata-ano-file-res",
        "error-toast-ano-file-res",
        "success-toast-ano-file-res",
    )

    return base + content


@callback(
    Output("datatable-ano-file-res", "data"),
    Output("datatable-ano-file-res", "columns"),
    Output("metadata-ano-file-res", "children"),
    Output("project-link-ano-file-res", "href"),
    Output("error-toast-ano-file-res", "children"),
    Output("error-toast-ano-file-res", "is_open"),
    Output("success-toast-ano-file-res", "children"),
    Output("success-toast-ano-file-res", "is_open"),
    Input("analysis-id-ano-file-res", "data"),
)
def populate_table(analysis_id):
    try:
        df_dict, columns, metadata_rows, project_id = populate_datatable(
            analysis_id)

        return (
            df_dict,
            columns,
            [html.Tbody(metadata_rows)],
            f"/dash/project/{project_id}",
            dash.no_update,
            False,
            dash.no_update,
            False,
        )

    except ValueError as e:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            str(e),
            True,
            dash.no_update,
            False,
        )
