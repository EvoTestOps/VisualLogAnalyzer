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
    path_template="/analysis/file-level-visualisations/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    layout = [
        dbc.Container(
            [
                html.H3("File Level Visualisation"),
                dcc.Store(id="analysis-id-file-res", data=analysis_id),
            ]
        )
    ] + create_high_level_viz_result_layout(
        "plot-content-file-res",
        "metadata-file-res",
        "error-toast-file-res",
        "success-toast-file-res",
    )
    return layout


@callback(
    Output("plot-content-file-res", "figure"),
    Output("plot-content-file-res", "style"),
    Output("metadata-file-res", "children"),
    Output("error-toast-file-res", "children"),
    Output("error-toast-file-res", "is_open"),
    Output("success-toast-file-res", "children"),
    Output("success-toast-file-res", "is_open"),
    Input("switch", "value"),
    State("analysis-id-file-res", "data"),
)
def create_plot(switch_on, analysis_id):
    try:
        fig, style, metadata_rows = create_high_level_plot(switch_on, analysis_id)
        return (
            fig,
            style,
            [html.Tbody(metadata_rows)],
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
