import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html
from dash_app.components.forms import file_level_viz_form
from dash_app.components.layouts import create_unique_term_count_layout
from dash_app.callbacks.callback_functions import create_high_level_plot

dash.register_page(
    __name__,
    path="/file-level-visualisations",
    title="File Level Visualisations",
)

form = file_level_viz_form(
    "submit_ut_file",
    "directory_ut_file",
    "analysis_type_ut_file",
    "mask_ut_file",
    "vectorizer_ut_file",
)
layout = [
    dbc.Container(html.H3("File Level Visualisations"))
] + create_unique_term_count_layout(
    form, "plot_content_ut_file", "error_toast_ut_file", "success_toast_ut_file"
)


@callback(
    Output("plot_content_ut_file", "figure"),
    Output("plot_content_ut_file", "style"),
    Output("error_toast_ut_file", "children"),
    Output("error_toast_ut_file", "is_open"),
    Output("success_toast_ut_file", "children"),
    Output("success_toast_ut_file", "is_open"),
    Input("submit_ut_file", "n_clicks"),
    Input("switch", "value"),
    State("directory_ut_file", "value"),
    State("analysis_type_ut_file", "value"),
    State("mask_ut_file", "value"),
    State("vectorizer_ut_file", "value"),
    prevent_initial_call=True,
)
def create_plot(
    n_clicks, switch_on, directory_path, terms_umap, mask_type, vectorizer_type
):
    return create_high_level_plot(
        n_clicks,
        switch_on,
        directory_path,
        terms_umap,
        mask_type,
        vectorizer_type,
        level="file",
    )
