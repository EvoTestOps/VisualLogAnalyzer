import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
from dash_app.components.forms import unique_terms_by_file_form
from dash_app.components.layouts import create_unique_term_count_layout
from dash_app.utils.plots import create_unique_term_count_plot_by_file

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
    prevent_initial_call=True,
)
def create_plot(n_clicks, switch_on, directory_path):
    if n_clicks == 0:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    buffer = None
    try:
        response = requests.post(
            "http://localhost:5000/api/run-unique-terms",
            json={"dir_path": directory_path, "file_level": True},
        )

        response.raise_for_status()

        parquet_bytes = io.BytesIO(response.content)
        df = pl.read_parquet(parquet_bytes)

        style = {
            "resize": "both",
            "overflow": "auto",
            "minHeight": "500px",
            "minWidth": "600px",
            "width": "90%",
        }

        if not switch_on:
            theme = "plotly_dark"
        else:
            theme = "plotly_white"

        fig = create_unique_term_count_plot_by_file(df, theme)

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

    finally:
        if buffer:
            buffer.close()
