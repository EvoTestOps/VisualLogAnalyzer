import dash
import polars as pl
import io
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dash_app.components.layouts import create_high_level_viz_layout
from dash_app.callbacks.callback_functions import make_api_call
from dash_app.utils.plots import create_files_count_plot

dash.register_page(
    __name__,
    path_template="/analysis/directory-level-visualisations/<analysis_id>",
)


def layout(analysis_id=None, **kwargs):
    layout = [
        dbc.Container(
            [
                html.H3("Directory Level Visualisations"),
                dcc.Store(id="analysis-id-ut-res", data=analysis_id),
            ]
        )
    ] + create_high_level_viz_layout(
        None, "plot-content-ut-res", "error-toast-ut-res", "success-toast-ut-res"
    )
    return layout


@callback(
    Output("plot-content-ut-res", "figure"),
    Output("plot-content-ut-res", "style"),
    Output("error-toast-ut-res", "children"),
    Output("error-toast-ut-res", "is_open"),
    Output("success-toast-ut-res", "children"),
    Output("success-toast-ut-res", "is_open"),
    Input("switch", "value"),
    State("analysis-id-ut-res", "data"),
)
def create_plot(switch_on, analysis_id):
    if not analysis_id:
        return (
            dash.no_update,
            dash.no_update,
            "No analysis id was provided",
            True,
            dash.no_update,
            False,
        )

    response, error = make_api_call({}, f"analyses/{analysis_id}", "GET")
    if error:
        return (dash.no_update, error, True, dash.no_update, False)

    df = pl.read_parquet(io.BytesIO(response.content))

    theme = "plotly_white" if switch_on else "plotly_dark"
    style = {
        "resize": "both",
        "overflow": "auto",
        "minHeight": "500px",
        "minWidth": "600px",
        "width": "90%",
    }
    fig = create_files_count_plot(df, theme)

    return fig, style, dash.no_update, False, "Success", True
