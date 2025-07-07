from dash import html


def format_key(key):
    return key.replace("_", " ").title()


def format_metadata_rows(metadata):
    metadata_rows = []
    for key, value in metadata.items():
        display_value = (
            value if value is not None else "-"
        )  # there shouldn't be any none values
        label = format_key(key)
        metadata_rows.append(html.Tr([html.Th(label), html.Td(display_value)]))
    return metadata_rows
