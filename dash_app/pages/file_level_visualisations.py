import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import unique_terms_by_file_form
from dash_app.components.layouts import create_unique_term_count_layout
from dash_app.utils.plots import create_unique_term_count_plot_by_file, create_umap_plot

dash.register_page(
    __name__,
    path="/file-level-visualisations",
    title="File Level Visualisations",
)

form = unique_terms_by_file_form()
layout = create_unique_term_count_layout(
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
    State("terms_umap_ut_file", "value"),
    prevent_initial_call=True,
)
def create_plot(n_clicks, switch_on, directory_path, terms_umap):
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
    }

    endpoint = endpoint_map.get(terms_umap, endpoint_map["umap"])
    url = f"http://localhost:5000/api/{endpoint}"

    try:
        response = requests.post(
            url,
            json={"dir_path": directory_path, "file_level": True},
        )
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

        if terms_umap == "terms":
            fig = create_unique_term_count_plot_by_file(df, theme)
        else:
            fig = create_umap_plot(df, "seq_id", theme)

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
