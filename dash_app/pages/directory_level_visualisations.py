import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import unique_terms_form
from dash_app.components.layouts import create_unique_term_count_layout
from dash_app.utils.plots import (
    create_unique_term_count_plot,
    create_files_count_plot,
    create_umap_plot,
)

dash.register_page(
    __name__,
    path="/directory-level-visualisations",
    title="Directory Level Visualisations",
)

form = unique_terms_form()
layout = create_unique_term_count_layout(
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
    State("terms_files_ut", "value"),
    prevent_initial_call=True,
)
def create_plot(n_clicks, switch_on, directory_path, terms_files):
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    endpoint_map = {
        "terms": "run-unique-terms",
        "umap": "umap",
        "default": "run-file-counts",
    }

    endpoint = endpoint_map.get(terms_files, endpoint_map["default"])
    url = f"http://localhost:5000/api/{endpoint}"

    try:
        response = requests.post(url, json={"dir_path": directory_path})
        response.raise_for_status()

        df = pl.read_parquet(io.BytesIO(response.content))

        theme = "plotly_white" if switch_on else "plotly_dark"
        style = {
            "resize": "both",
            "overflow": "auto",
            "minHeight": "500px",
            "minWidth": "600px",
            "width": "90%",
        }

        if terms_files == "terms":
            fig = create_unique_term_count_plot(df, theme)
        elif terms_files == "umap":
            fig = create_umap_plot(df, "run", theme)
        else:
            fig = create_files_count_plot(df, theme)

        return (
            fig,
            style,
            "",
            False,
            "Analysis complete.",
            True,
        )

    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json().get("error", str(e))
        except Exception:
            error_message = str(e)

        return (
            dash.no_update,
            dash.no_update,
            error_message,
            True,
            dash.no_update,
            False,
        )
