from datetime import datetime
from dash import html
import dash_bootstrap_components as dbc


def _format_key(key, divider="_"):
    return key.replace(divider, " ").title()


def _format_iso_time(timestamp: str):
    try:
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime("%d.%m.%Y %H:%M:%S")
    except ValueError:
        return timestamp


def format_metadata_rows(metadata):
    metadata_rows = []
    for key, value in metadata.items():
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
