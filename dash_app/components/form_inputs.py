import dash_bootstrap_components as dbc
from dash import dcc, html


def log_format_input(id):
    return dbc.Col(
        [
            dbc.Label("Log Format", html_for=id, width="auto"),
            dbc.Select(
                id=id,
                options=[
                    {"label": "LO2", "value": "lo2"},
                    {"label": "Raw", "value": "raw"},
                    # {"label": "Hadoop", "value": "hadoop"},
                ],
            ),
        ],
    )


def directory_input(id):
    return dbc.Col(
        [
            dbc.Label("Directory Path", html_for=id, width="auto"),
            dbc.Input(type="text", id=id, placeholder="path/to/your/root/log/folder"),
        ]
    )


def train_data_input(id):
    return dbc.Col(
        [
            dbc.Label("Directory path to train data", html_for=id, width="auto"),
            dbc.Input(
                type="text", id=id, placeholder="path/to/your/train/data/directory"
            ),
        ]
    )


def test_data_input(id):
    return dbc.Col(
        [
            dbc.Label("Directory path to test data", html_for=id, width="auto"),
            dbc.Input(
                type="text", id=id, placeholder="path/to/your/test/data/directory"
            ),
        ]
    )


def detectors_input(id):
    return dbc.Col(
        [
            dbc.Label("Detectors", html_for=id, width="auto"),
            dcc.Dropdown(
                options=[
                    {"label": "Logistic Regression", "value": "lr"},
                    {"label": "Decision Tree", "value": "dt"},
                    {"label": "K-Means", "value": "kmeans"},
                    {"label": "Rarity Model", "value": "rm"},
                    {"label": "OOVD", "value": "oovd"},
                    {"label": "Isolation Forest", "value": "if"},
                ],
                multi=True,
                id=id,
                className="dbc border border-light-subtle rounded",
            ),
        ],
    )


def enhancement_input(id):
    return dbc.Col(
        [
            dbc.Label("Enhancement", html_for=id, width="auto"),
            dbc.Select(
                id=id,
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


def sequence_input(id):
    return dbc.Col(
        [
            dbc.Label("Event/Seq", html_for=id, width="auto"),
            dbc.RadioItems(
                id=id,
                options=[
                    {"label": "Event", "value": False},
                    {"label": "Sequence", "value": True},
                ],
                value=False,
                inline=True,
            ),
        ]
    )


def test_frac_input(id):
    return dbc.Row(
        [
            dbc.Label("Test fraction", html_for=id),
            dcc.Slider(id=id, min=0.0, max=1.0, step=0.1, value=0.9),
        ],
        class_name="dbc mb-3",
    )


def submit_button(id, label):
    return dbc.Button(label, id=id, n_clicks=0)
