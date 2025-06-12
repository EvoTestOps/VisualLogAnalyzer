import dash_bootstrap_components as dbc
from dash import dcc


def log_format_input():
    return dbc.Col(
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


def directory_input():
    return dbc.Col(
        [
            dbc.Label("Directory Path", html_for="directory", width="auto"),
            dbc.Input(
                type="text", id="directory", placeholder="path/to/your/root/log/folder"
            ),
        ]
    )


def detectors_input():
    return dbc.Col(
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
                className="dbc",
            ),
        ]
    )


def enhancement_input():
    return dbc.Col(
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


def sequence_input():
    return dbc.Col(
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


def test_frac_input():
    return dbc.Row(
        [
            dbc.Label("Test fraction", html_for="test_frac"),
            dcc.Slider(id="test_frac", min=0.0, max=1.0, step=0.1, value=0.9),
        ],
        class_name="mb-3",
    )
