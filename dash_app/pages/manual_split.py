import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
import requests
from dash import Input, Output, State, callback, dcc, html
import io
from dash_app.components.form_inputs import (
    log_format_input,
    directory_input,
    detectors_input,
    enhancement_input,
    sequence_input,
    test_frac_input,
    train_data_input,
    test_data_input,
)

dash.register_page(__name__, path="/manual-split", title="Manual Split")

plot_tr = html.Div(dcc.Graph(id="plot_area_tr"))
submit_btn_tr = dbc.Button("Submit", id="submit_tr", n_clicks=0, class_name="mb-3")

form_tr = dbc.Form(
    [
        dbc.Row(
            [
                log_format_input("log_format_tr"),
                train_data_input("train_data_tr"),
                test_data_input("test_data_tr"),
            ],
            class_name="mb-3",
        ),
        dbc.Row(
            [
                detectors_input("detectors_tr"),
                enhancement_input("enhancement_tr"),
                sequence_input("sequence_tr"),
            ],
            class_name="mb-3",
        ),
        submit_btn_tr,
    ],
    class_name="border border-primary-subtle p-3 mb-3",
)

layout = dbc.Container([form_tr, plot_tr])


@callback(
    Output("plot_area_tr", "figure"),
    Input("submit_tr", "n_clicks"),
    State("log_format_tr", "value"),
    State("train_data_tr", "value"),
    State("test_data_tr", "value"),
    State("detectors_tr", "value"),
    State("enhancement_tr", "value"),
    State("sequence_tr", "value"),
    prevent_initial_call=True,
)
def update_plot_test_train(
    n_clicks,
    log_format,
    train_data,
    test_data,
    detectors,
    enhancement,
    sequence,
):
    return px.scatter(title="TR Plot")
