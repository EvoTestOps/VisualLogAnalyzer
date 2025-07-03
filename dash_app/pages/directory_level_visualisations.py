import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html
from dash_app.components.forms import directory_level_viz_form
from dash_app.components.layouts import create_high_level_viz_layout
from dash_app.callbacks.callback_functions import create_high_level_plot

dash.register_page(
    __name__,
    path="/directory-level-visualisations",
    title="Directory Level Visualisations",
)

form = directory_level_viz_form(
    "submit_ut", "directory_ut", "analysis_type_ut", "mask_ut", "vectorizer_ut"
)
layout = [
    dbc.Container(html.H3("Directory Level Visualisations"))
] + create_high_level_viz_layout(
    form, "plot_content_ut", "error_toast_ut", "success_toast_ut"
)


@callback(
    Output("plot_content_ut", "figure"),
    Output("plot_content_ut", "style"),
    Output("error_toast_ut", "children"),
    Output("error_toast_ut", "is_open"),
    Output("success_toast_ut", "children"),
    Output("success_toast_ut", "is_open"),
    Input("submit_ut", "n_clicks"),
    Input("switch", "value"),
    State("directory_ut", "value"),
    State("analysis_type_ut", "value"),
    State("mask_ut", "value"),
    State("vectorizer_ut", "value"),
    prevent_initial_call=True,
)
def create_plot(
    n_clicks, switch_on, directory_path, terms_files, mask_type, vectorizer_type
):
    return create_high_level_plot(
        n_clicks,
        switch_on,
        directory_path,
        terms_files,
        mask_type,
        vectorizer_type,
        level="run",
    )
