import dash_bootstrap_components as dbc


def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Labeled", href="/dash/labeled")),
            dbc.NavItem(dbc.NavLink("Manual Split", href="/dash/manual-split")),
        ]
    )
