import dash_bootstrap_components as dbc


def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Home", href="/dash/")),
            # dbc.NavItem(dbc.NavLink("Labeled", href="/dash/labeled")),
            dbc.NavItem(dbc.NavLink("Manual Split", href="/dash/manual-split")),
            dbc.NavItem(
                dbc.NavLink(
                    "Directory Level Visualisations",
                    href="/dash/directory-level-visualisations",
                )
            ),
        ],
        class_name="h5",
    )
