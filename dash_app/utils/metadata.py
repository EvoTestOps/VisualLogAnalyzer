from datetime import datetime

import dash_bootstrap_components as dbc
from dash import html


def _format_key(key, divider="_"):
    return key.replace(divider, " ").title()


def _format_iso_time(timestamp: str):
    try:
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return timestamp


def format_metadata_rows(metadata):
    metadata_rows = []
    for key, value in metadata.items():
        if key in ("time_created", "time_updated"):
            value = _format_iso_time(value)

        display_value = (
            value if value is not None else "-"
        )  # there shouldn't be any none values
        label = _format_key(key)
        metadata_rows.append(html.Tr([html.Th(label), html.Td(display_value)]))
    return metadata_rows


def format_analysis_overview(analyses_data):
    analyses_data = sorted(analyses_data, key=lambda d: d["time_created"], reverse=True)
    group_items = [
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H4(
                            _format_key(analysis["analysis_sub_type"], divider="-"),
                            className="mb-0",
                        ),
                        html.P(_format_iso_time(analysis["time_created"])),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.P(f"Level: {_format_key(analysis['analysis_level'])}"),
            ],
            href=f"/dash/analysis/{analysis['analysis_type']}/{analysis['id']}",
            class_name="pb-3 pt-3",
        )
        for analysis in analyses_data
    ]

    return group_items


def format_project_overview(project_data):
    project_data = sorted(project_data, key=lambda d: d["time_created"], reverse=True)
    group_items = [
        dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H4(project["name"], className="mb-0"),
                        html.P(_format_iso_time(project["time_created"])),
                    ],
                    className="d-flex justify-content-between align-items-center",
                ),
                html.P(f"Amount of analyses: {(project['analyses_count'])}"),
            ],
            href=f"/dash/project/{project['id']}?project_name={project['name']}",
            class_name="pb-3 pt-3",
        )
        for project in project_data
    ]
    return group_items
