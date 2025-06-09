import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
import requests
from dash import Input, Output, State, callback, dcc, html

dash.register_page(__name__, path="/", title="home")


dataset_input = html.Div(
    [
        dbc.Label("Dataset", html_for="dataset", width=2),
        dbc.Select(
            id="dataset",
            options=[
                {"label": "LO2", "value": "lo2"},
                {"label": "Raw", "value": "raw"},
            ],
        ),
    ],
    className="mb-3",
)

directory_input = html.Div(
    [
        dbc.Label("Log Directory", html_for="directory", width=2),
        dbc.Input(
            type="text", id="directory", placeholder="path/to/your/root/log/folder"
        ),
    ],
    className="mb-3",
)

submit_btn = dbc.Button("Submit", id="submit", n_clicks=0)

plot = html.Div(dcc.Graph(id="plot-area"))

form = dbc.Form([dataset_input, directory_input, submit_btn])
layout = dbc.Container([form, plot])


@callback(
    Output("plot-area", "figure"),
    Input("submit", "n_clicks"),
    State("dataset", "value"),
    State("directory", "value"),
    prevent_initial_call=True,
)
def update_plot(n_clicks, dataset, directory):
    try:
        response = requests.post(
            "http://localhost:5000/api/simple_plot",
            params={"dataset": dataset, "directory": directory},
        )
        response.raise_for_status()

        data = response.json()
        df = pl.from_dicts(data)

        fig = px.scatter(
            df,
            x="file_count",
            y="line_count",
            hover_data=["file_count", "line_count", "run"],
        )

        return fig

    except Exception as e:
        return px.scatter(title=f"Error loading data: {e}")
