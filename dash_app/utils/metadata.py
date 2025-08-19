from datetime import datetime, timezone
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
        return datetime_obj.strftime("%H:%M %d.%m.%Y")
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
        elif key == "match_filenames":
            if value == "None":
                continue

        display_value = value if value is not None else "-"
        label = _format_key_capitalize(key)
        metadata_rows.append(html.Tr([html.Th(label), html.Td(display_value)]))

    return metadata_rows


def _sort_metadata(metadata: dict) -> dict:
    order = [
        "name",
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
        "match_filenames",
        "results_path",
        "time_created",
        # "time_updated",
    ]

    return {key: metadata[key] for key in order if key in metadata}


def format_analysis_overview(analyses_data: list[dict]) -> list[dbc.ListGroupItem]:

    analyses_data = sorted(analyses_data, key=lambda d: d["time_created"], reverse=True)

    group_items = []

    for analysis in analyses_data:
        analysis_id = analysis["id"]
        analysis_name = analysis.get("name")
        sub_type_title = _format_key_title(analysis["analysis_sub_type"], divider="-")
        level_title = _format_key_title(analysis["analysis_level"])
        created_time = _format_iso_time(analysis["time_created"])
        analysis_url = f"/dash/analysis/{analysis['analysis_type']}/{analysis['id']}"

        title_block = [html.H4(analysis_name or sub_type_title, className="mb-0")]

        bottom_left_items = []

        edit_dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    "Edit name",
                    id={"type": "edit-button", "index": str(analysis_id)},
                    n_clicks=0,
                ),
                dbc.DropdownMenuItem(
                    "Delete",
                    id={"type": "delete-button", "index": str(analysis_id)},
                    n_clicks=0,
                ),
            ],
            label="⋮",
            color="secondary",
            caret=False,
        )

        if analysis_name:
            bottom_left_items.append(
                html.P(f"Type: {sub_type_title}", className="mb-0")
            )

        bottom_left_items.append(html.P(f"Level: {level_title}", className="mb-0"))

        item = dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.A(title_block, href=analysis_url),
                        html.P(created_time),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.Div(
                    [
                        html.Div(bottom_left_items),
                        edit_dropdown,
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
            ],
            class_name="pb-3 pt-3",
        )

        group_items.append(item)

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
                            href=f"/dash/project/{project['id']}",
                        ),
                        html.P(_format_iso_time(project["time_created"])),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    f"Base path: {(project.get('base_path') or "log_data").lstrip("/app/")}",
                                    className="mb-0",
                                ),
                                html.P(
                                    f"Amount of analyses: {(project['analyses_count'])}",
                                    className="mb-0",
                                ),
                            ]
                        ),
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


def _format_elapsed_seconds(seconds: int):
    if seconds < 60:
        return f"{seconds} sec"
    else:
        return f"{int(seconds / 60)} min"


def _format_start_time(timestamp: str) -> str:
    try:
        utc_time = datetime.fromisoformat(timestamp)
        # Should convert to system time but not sure how consistent it is with docker
        corrected_time = utc_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
        return corrected_time.strftime("%H:%M")
    except Exception:
        return timestamp


def format_task_overview_row(task_id: str, meta: dict, state: str) -> html.Tr:
    match state:
        case "STARTED" | "PENDING" | "PROGRESS":
            task_state = html.Span(
                "Running",
                id={"type": "task-logs", "index": task_id},
                style={"cursor": "pointer", "textDecoration": "underline"},
                n_clicks=0,
            )
        case "SUCCESS":
            task_state = html.Span(
                "Success",
                id={"type": "task-logs", "index": task_id},
                style={"cursor": "pointer", "textDecoration": "underline"},
                n_clicks=0,
            )
        case "FAILURE":
            task_state = html.Span(
                "Failed",
                id={"type": "task-error", "index": task_id},
                style={"cursor": "pointer", "textDecoration": "underline"},
                n_clicks=0,
            )
        case _:
            task_state = "unknown"

    formatted_time = _format_elapsed_seconds(meta.get("elapsed_seconds", 0))
    start_time = _format_start_time(str(meta.get("start_time")))

    row_content = [
        html.Td(f"{meta.get("analysis_type", "unknown")}"),
        html.Td(task_state),
        html.Td(start_time),
        html.Td(formatted_time),
    ]

    return html.Tr(row_content)


def parse_query_parameter(search: str, param_name: str) -> str | None:
    query = parse_qs(search.lstrip("?"))
    result = query.get(param_name, [None])[0]

    return result
