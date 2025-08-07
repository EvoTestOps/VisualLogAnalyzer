import dash_bootstrap_components as dbc
from dash import dcc, html


def log_format_input(id):
    return dbc.Col(
        [
            dbc.Label("Log Format", html_for=id, width="auto"),
            dbc.Select(
                id=id,
                options=[
                    {"label": "Raw", "value": "raw"},
                    # {"label": "LO2", "value": "lo2"},
                ],
                value="raw",
            ),
        ],
    )


def directory_dropdown_input(id, label="Directory"):
    return dbc.Col(
        [
            dbc.Label(label, html_for=id, width="auto"),
            dcc.Dropdown(
                id=id,
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def detectors_unsupervised_input(id):
    return dbc.Col(
        [
            dbc.Label("Detectors", html_for=id, width="auto"),
            dcc.Dropdown(
                options=[
                    {"label": "K-Means", "value": "kmeans"},
                    {"label": "Rarity Model", "value": "rm"},
                    {"label": "OOVD", "value": "oovd"},
                    {"label": "Isolation Forest", "value": "if"},
                ],
                value=["kmeans", "rm", "oovd", "if"],
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
                value="e_words",
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


def delete_button(id, label):
    return dbc.Button(
        label, color="danger", id={"type": "delete-button", "index": id}, n_clicks=0
    )


def runs_filter_input(id, manual=False):
    if manual:
        return dbc.Col(
            [
                dbc.Label(
                    "Runs to include in test data (manual, comma-separated)",
                    html_for=id,
                    width="auto",
                ),
                dbc.Input(
                    type="text",
                    id=id,
                    placeholder="e.g. ./log_data/LO2/correct_1/log_file.log, ./log_data/LO2/correct_2/log_file_2.log ...",
                ),
            ],
        )
    return dbc.Col(
        [
            dbc.Label("Runs to include in test data", html_for=id, width="auto"),
            dcc.Dropdown(
                multi=True,
                id=id,
                placeholder="Defaults to all runs",
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def files_filter_input(id, manual=False):
    if manual:
        return dbc.Col(
            [
                dbc.Label(
                    "Files to include in test data (manual, comma-separated)",
                    html_for=id,
                    width="auto",
                ),
                dbc.Input(
                    type="text",
                    id=id,
                    placeholder="e.g. ./log_data/LO2/correct_1/log_file.log, ./log_data/LO2/correct_2/log_file_2.log ...",
                ),
            ],
        )
    return dbc.Col(
        [
            dbc.Label("Files to include in test data", html_for=id, width="auto"),
            dcc.Dropdown(
                multi=True,
                id=id,
                placeholder="Defaults to all files",
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def target_run_input(id, manual=False):
    if manual:
        return dbc.Col(
            [
                dbc.Label(
                    "Target run",
                    html_for=id,
                    width="auto",
                ),
                dbc.Input(
                    type="text",
                    id=id,
                    placeholder="e.g. ./log_data/LO2/correct_1/log_file.log",
                ),
            ],
        )

    return dbc.Col(
        [
            dbc.Label("Target run", html_for=id, width="auto"),
            dcc.Dropdown(
                id=id,
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def terms_files_input(id):
    return dbc.Col(
        [
            dbc.Label("Type", html_for=id, width="auto"),
            dbc.RadioItems(
                id=id,
                options=[
                    {"label": "Terms & Lines", "value": "terms"},
                    {"label": "Files & Lines", "value": "files"},
                    {"label": "UMAP", "value": "umap"},
                ],
                value="terms",
                inline=True,
            ),
        ]
    )


def terms_umap_input(id):
    return dbc.Col(
        [
            dbc.Label("Type", html_for=id, width="auto"),
            dbc.RadioItems(
                id=id,
                options=[
                    {"label": "Terms & Lines", "value": "terms"},
                    {"label": "UMAP", "value": "umap"},
                ],
                value="terms",
                inline=True,
            ),
        ]
    )


def mask_input(id):
    return dbc.Col(
        [
            dbc.Label("Regex mask type", html_for=id, width="auto"),
            dcc.Dropdown(
                options=[
                    {"label": "Myllari", "value": "myllari"},
                    {"label": "Myllari Extended", "value": "myllari_extended"},
                    {"label": "Drain LogLead", "value": "drain_loglead"},
                    {"label": "Drain Original", "value": "drain_orig"},
                ],
                id=id,
                placeholder="Optional",
                className="dbc border border-light-subtle rounded",
            ),
        ],
    )


def vectorizer_input(id):
    return dbc.Col(
        [
            dbc.Label("Vectorizer type", html_for=id, width="auto"),
            dbc.Select(
                id=id,
                options=[
                    {"label": "Count", "value": "count"},
                    {"label": "TF-IDF", "value": "tfidf"},
                ],
                value="count",
            ),
        ],
    )


def name_input(id):
    return dbc.Col(
        [
            dbc.Label("Project name", html_for=id, width="auto"),
            dbc.Input(
                type="text",
                id=id,
            ),
        ]
    )


def match_file_names_input(id):
    return dbc.Col(
        [
            dbc.Checkbox(
                id=id,
                label=html.Span(
                    "Match filenames",
                    id=f"{id}-label",
                    style={"textDecoration": "underline", "cursor": "pointer"},
                ),
            ),
            dbc.Tooltip(
                "Enable this setting to automatically match filenames against baseline runs in file and line level analysis.",
                target=f"{id}-label",
                placement="bottom",
            ),
        ]
    )


def color_by_directory_input(id):
    return dbc.Col(
        [
            dbc.Checkbox(
                id=id,
                label=html.Span(
                    "Color datapoints by directory",
                    id=f"{id}-label",
                    style={"textDecoration": "underline", "cursor": "pointer"},
                ),
            ),
            dbc.Tooltip(
                "Color datapoints in file level analysis by directory.",
                target=f"{id}-label",
                placement="bottom",
            ),
        ]
    )


def line_display_mode_input(id):
    return dbc.Col(
        html.Div(
            [
                dbc.Label("Line level display options"),
                dbc.RadioItems(
                    options=[
                        {"label": "Data points only", "value": "data_points_only"},
                        {"label": "Moving averages only", "value": "moving_avg_only"},
                        {"label": "Show all", "value": "all"},
                    ],
                    value="data_points_only",
                    id=id,
                ),
            ],
            className="mt-3",
        )
    )


def manual_filename_input(id):
    return dbc.Col(
        [
            dbc.Checkbox(
                id=id,
                label=html.Span(
                    "Manual filename entry",
                    id=f"{id}-label",
                    style={"textDecoration": "underline", "cursor": "pointer"},
                ),
            ),
            dbc.Tooltip(
                "Filenames are not generated to dropdown automatically. Avoids blocking UI and slow generation times.",
                target=f"{id}-label",
                placement="bottom",
            ),
        ]
    )


def redirect_to_results_input(id):
    return dbc.Col(
        [
            dbc.Switch(
                id=id,
                label=html.Span(
                    "Open results when ready",
                    id=f"{id}-label",
                    style={"textDecoration": "underline", "cursor": "pointer"},
                ),
                value=False,
            ),
            dbc.Tooltip(
                "If on, will redirect instantly to analysis results when they are ready. Otherwise will redirect back to project page.",
                target=f"{id}-label",
                placement="bottom",
            ),
        ]
    )


def files_to_include_input(id):
    return dbc.Col(
        [
            dbc.Label("Files to include (2-8)", html_for=id, width="auto"),
            dcc.Dropdown(
                multi=True,
                id=id,
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def columns_to_include_input(id):
    return dbc.Col(
        [
            dbc.Label("Columns to include", html_for=id, width="auto"),
            dcc.Dropdown(
                multi=True,
                id=id,
                className="dbc border border-light-subtle rounded",
                optionHeight=40,
                maxHeight=350,
            ),
        ],
    )


def analysis_name_input(id):
    return dbc.Col(
        [
            dbc.Label("Columns to include", html_for=id, width="auto"),
            dbc.Input(id=id, placeholder="Optional", type="text"),
        ],
    )
