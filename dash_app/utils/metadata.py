from datetime import datetime
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
from dash import html

from dash_app.components.form_inputs import delete_button


def _format_key_title(key: str, divider="_") -> str:
    return key.replace(divider, " ").title()


def _format_key_capitalize(key: str, divider="_") -> str:
    return key.replace(divider, " ").capitalize()


def _format_iso_time(timestamp: str) -> str:
    try:
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return timestamp


def _format_model(model: str) -> str:
    match model:
        case "kmeans":
            return "K-Means"
        case "rm":
            return "Rarity Model"
        case "if":
            return "Isolation Forest"
        case "oovd":
            return "Out-of-Vocabulary Detector"
        case _:
            return model


def format_metadata_rows(metadata: dict) -> list[html.Tr]:
    metadata = _sort_metadata(metadata)
    metadata_rows = []

    for key, value in metadata.items():
        if key in ("time_created", "time_updated"):
            value = _format_iso_time(value)
        elif key == "models":
            models = value.split(";")
            formatted_models = [_format_model(model) for model in models]
            value = ", ".join(formatted_models)

        display_value = value if value is not None else "-"
        label = _format_key_capitalize(key)
        metadata_rows.append(html.Tr([html.Th(label), html.Td(display_value)]))

    return metadata_rows


def _sort_metadata(metadata: dict) -> dict:
    order = [
        "analysis_type",
        "analysis_sub_type",
        "analysis_level",
        "directory_path",
        "train_data_path",
        "test_data_path",
        "models",
        "enhancement",
        "target",
        "field",
        "mask_type",
        "vectorizer",
        "results_path",
        "time_created",
        # "time_updated",
    ]

    return {key: metadata[key] for key in order if key in metadata}


def format_analysis_overview(analyses_data: list[dict]) -> list[dbc.ListGroupItem]:

    analyses_data = sorted(analyses_data, key=lambda d: d["time_created"], reverse=True)
    group_items = [
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.A(
                            html.H4(
                                _format_key_title(
                                    analysis["analysis_sub_type"], divider="-"
                                ),
                                className="mb-0",
                            ),
                            href=f"/dash/analysis/{analysis['analysis_type']}/{analysis['id']}",
                        ),
                        html.P(_format_iso_time(analysis["time_created"])),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.Div(
                    [
                        html.P(
                            f"Level: {_format_key_title(analysis['analysis_level'])}"
                        ),
                        delete_button(id=str(analysis["id"]), label="Delete"),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
            ],
            class_name="pb-3 pt-3",
        )
        for analysis in analyses_data
    ]

    return group_items


def format_project_overview(project_data: list[dict]) -> list[dbc.ListGroupItem]:
    project_data = sorted(project_data, key=lambda d: d["time_created"], reverse=True)
    group_items = [
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.A(
                            html.H4(project["name"], className="mb-0"),
                            href=f"/dash/project/{project['id']}?project_name={project['name']}",
                        ),
                        html.P(_format_iso_time(project["time_created"])),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.Div(
                    [
                        html.P(f"Amount of analyses: {(project['analyses_count'])}"),
                        delete_button(id=str(project["id"]), label="Delete"),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
            ],
            class_name="pb-3 pt-3",
        )
        for project in project_data
    ]
    return group_items


def parse_query_parameter(search: str, param_name: str) -> str | None:
    query = parse_qs(search.lstrip("?"))
    result = query.get(param_name, [None])[0]

    return result
