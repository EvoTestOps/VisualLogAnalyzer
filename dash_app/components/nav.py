import dash_bootstrap_components as dbc


def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Home", href="/dash/")),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("Run Level", href="/dash/ano-run-level"),
                    dbc.DropdownMenuItem("Line Level", href="/dash/ano-line-level"),
                ],
                label="Anomaly Detection",
                nav=True,
            ),
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem(
                        "Directory Level", href="/dash/directory-level-visualisations"
                    ),
                    dbc.DropdownMenuItem(
                        "File Level", href="/dash/file-level-visualisations"
                    ),
                ],
                label="High level Visualisations",
                nav=True,
            ),
        ],
        class_name="h5",
    )
