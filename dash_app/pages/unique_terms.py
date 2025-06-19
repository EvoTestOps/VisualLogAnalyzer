import dash
import polars as pl
import requests
from dash import Input, Output, State, callback
import io
import base64
from dash_app.components.forms import unique_terms_form
from dash_app.components.layouts import create_unique_term_count_layout
from dash_app.utils.plots import create_unique_term_count_plot

dash.register_page(__name__, path="/unique-terms", title="Unique Terms Analysis")

form = unique_terms_form()
layout = create_unique_term_count_layout(
    form, "plot_content_ut", "error_toast_ut", "success_toast_ut"
)


@callback(
    # Output("stored_data_tr", "data"),
    Output("plot_content_ut", "figure"),
    Output("plot_content_ut", "style"),
    Output("error_toast_ut", "children"),
    Output("error_toast_ut", "is_open"),
    Output("success_toast_ut", "children"),
    Output("success_toast_ut", "is_open"),
    Input("submit_ut", "n_clicks"),
    Input("switch", "value"),
    State("directory_ut", "value"),
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
            json={"dir_path": directory_path},
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

        fig = create_unique_term_count_plot(df, theme)

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
