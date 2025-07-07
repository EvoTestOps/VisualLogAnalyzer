import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html
from dash_app.components.layouts import (
    create_datatable_layout,
)
from dash_app.callbacks.callback_functions import (
    populate_datatable,
)

dash.register_page(
    __name__,
    path_template="/analysis/distance-file-level/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    layout = [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H3("Distance File Level")),
                        dbc.Col(
                            dcc.Link(
                                "Back to project",
                                id="project-link-dis-res-file",
                                href="/dash/project",
                            ),
                            className="d-flex justify-content-end",
                        ),
                    ]
                ),
                dcc.Store(id="analysis-id-dis-res-file", data=analysis_id),
            ],
        )
    ] + create_datatable_layout(
        "datatable-dis-res-file",
        "metadata-dis-res-file",
        "error-toast-dis-res-file",
        "success-toast-dis-res-file",
    )
    return layout


@callback(
    Output("datatable-dis-res-file", "data"),
    Output("datatable-dis-res-file", "columns"),
    Output("metadata-dis-res-file", "children"),
    Output("project-link-dis-res-file", "href"),
    Output("error-toast-dis-res-file", "children"),
    Output("error-toast-dis-res-file", "is_open"),
    Output("success-toast-dis-res-file", "children"),
    Output("success-toast-dis-res-file", "is_open"),
    Input("analysis-id-dis-res-file", "data"),
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
