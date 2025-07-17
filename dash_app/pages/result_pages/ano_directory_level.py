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
    path_template="/analysis/ano-directory-level/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    base = create_result_base_layout(
        "Anomaly Detection Directory Level",
        analysis_id,
        "project-link-ano-dir-res",
        "analysis-id-ano-dir-res",
    )
    content = create_datatable_layout(
        "datatable-ano-dir-res",
        "metadata-ano-dir-res",
        "error-toast-ano-dir-res",
        "success-toast-ano-dir-res",
    )

    return base + content


@callback(
    Output("datatable-ano-dir-res", "data"),
    Output("datatable-ano-dir-res", "columns"),
    Output("metadata-ano-dir-res", "children"),
    Output("project-link-ano-dir-res", "href"),
    Output("error-toast-ano-dir-res", "children"),
    Output("error-toast-ano-dir-res", "is_open"),
    Output("success-toast-ano-dir-res", "children"),
    Output("success-toast-ano-dir-res", "is_open"),
    Input("analysis-id-ano-dir-res", "data"),
)
def populate_table(analysis_id):
    try:
        df_dict, columns, metadata_rows, project_id = populate_datatable(analysis_id)

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
