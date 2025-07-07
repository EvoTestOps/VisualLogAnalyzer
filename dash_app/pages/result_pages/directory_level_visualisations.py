import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dash_app.components.layouts import (
    create_high_level_viz_result_layout,
)
from dash_app.callbacks.callback_functions import (
    create_high_level_plot,
)

dash.register_page(
    __name__,
    path_template="/analysis/directory-level-visualisations/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    layout = [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(html.H3("Directory Level Visualisation")),
                        dbc.Col(
                            dcc.Link(
                                "Back to project",
                                id="project-link-ut-res",
                                href="/dash/project",
                            ),
                            className="d-flex justify-content-end",
                        ),
                    ]
                ),
                dcc.Store(id="analysis-id-ut-res", data=analysis_id),
            ],
        )
    ] + create_high_level_viz_result_layout(
        "plot-content-ut-res",
        "metadata-ut-res",
        "error-toast-ut-res",
        "success-toast-ut-res",
    )
    return layout


@callback(
    Output("plot-content-ut-res", "figure"),
    Output("plot-content-ut-res", "style"),
    Output("metadata-ut-res", "children"),
    Output("project-link-ut-res", "href"),
    Output("error-toast-ut-res", "children"),
    Output("error-toast-ut-res", "is_open"),
    Output("success-toast-ut-res", "children"),
    Output("success-toast-ut-res", "is_open"),
    Input("switch", "value"),
    State("analysis-id-ut-res", "data"),
)
def create_plot(switch_on, analysis_id):
    try:
        fig, style, metadata_rows, project_id = create_high_level_plot(
            switch_on, analysis_id
        )
        return (
            fig,
            style,
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
            dash.no_update,
            str(e),
            True,
            dash.no_update,
            False,
        )
