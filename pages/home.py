import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl
import requests
from dash import Input, Output, State, callback, dcc, html
import io

dash.register_page(__name__, path="/", title="home")


log_format_input = dbc.Col(
    [
        dbc.Label("Log Format", html_for="log_format", width="auto"),
        dbc.Select(
            id="log_format",
            options=[
                {"label": "LO2", "value": "lo2"},
                {"label": "Hadoop", "value": "hadoop"},
            ],
        ),
    ],
)

directory_input = dbc.Col(
    [
        dbc.Label("Directory Path", html_for="directory", width="auto"),
        dbc.Input(
            type="text", id="directory", placeholder="path/to/your/root/log/folder"
        ),
    ]
)

detectors_input = dbc.Col(
    [
        dbc.Label("Detectors", html_for="detectors", width="auto"),
        dcc.Dropdown(
            options=[
                {"label": "Logistic Regression", "value": "lr"},
                {"label": "Decision Tree", "value": "dt"},
                {"label": "K-Means", "value": "kmeans"},
                {"label": "Rarity Model", "value": "rm"},
                {"label": "OOVD", "value": "oovd"},
            ],
            multi=True,
            id="detectors",
        ),
    ]
)

enhancement_input = dbc.Col(
    [
        dbc.Label("Enhancement", html_for="enhancement", width="auto"),
        dbc.Select(
            id="enhancement",
            options=[
                {"label": "Words", "value": "e_words"},
                {"label": "Trigrams", "value": "e_trigrams"},
                {"label": "Drain", "value": "e_event_drain_id"},
                {"label": "Tip", "value": "e_event_tip_id"},
                {"label": "Brain", "value": "e_event_brain_id"},
                {"label": "Pliplom", "value": "e_event_pliplom_id"},
                {"label": "Iplom", "value": "e_event_iplom_id"},
            ],
        ),
    ]
)

sequence_input = dbc.Col(
    [
        dbc.Label("Event/Seq", html_for="sequence", width="auto"),
        dbc.RadioItems(
            id="sequence",
            options=[
                {"label": "Event", "value": False},
                {"label": "Sequence", "value": True},
            ],
            inline=True,
        ),
    ]
)

test_frac_input = dbc.Row(
    [
        dbc.Label("Test fraction", html_for="test_frac"),
        dcc.Slider(id="test_frac", min=0.0, max=1.0, step=0.1, value=0.9),
    ],
    class_name="mb-3",
)


submit_btn = dbc.Button("Submit", id="submit", n_clicks=0, class_name="mb-3")

plot = html.Div(dcc.Graph(id="plot-area"))

form = dbc.Form(
    [
        dbc.Row([log_format_input, directory_input], class_name="mb-3"),
        dbc.Row(
            [detectors_input, enhancement_input, sequence_input], class_name="mb-3"
        ),
        test_frac_input,
        submit_btn,
    ],
    class_name="border border-primary-subtle p-3",
)

layout = dbc.Container([form, plot])


@callback(
    Output("plot-area", "figure"),
    Input("submit", "n_clicks"),
    State("log_format", "value"),
    State("directory", "value"),
    State("detectors", "value"),
    State("enhancement", "value"),
    State("sequence", "value"),
    State("test_frac", "value"),
    prevent_initial_call=True,
)
def update_plot(
    n_clicks, log_format, directory, detectors, enhancement, sequence, test_frac
):
    try:
        response = requests.post(
            "http://localhost:5000/api/analyze",
            json={
                "dir_path": directory,
                "log_format": log_format,
                "models": detectors,
                "item_list_col": enhancement,
                "test_frac": test_frac,
                "seq": sequence,
            },
        )
        response.raise_for_status()
        parquet_bytes = io.BytesIO(response.content)
        df = pl.read_parquet(parquet_bytes)

        return px.scatter(title="OK")

    except Exception as e:
        return px.scatter(title=f"Error loading data: {e}")
