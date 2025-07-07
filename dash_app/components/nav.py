from dash import html
import dash_bootstrap_components as dbc


def nav():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Projects", href="/dash/")),
        ],
        class_name="h4",
    )


def crate_analysis_nav(project_id, nav_id):
    return html.Div(
        [
            dbc.Label(html.H4("Create a new analysis"), html_for=nav_id),
            dbc.Nav(
                [
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/ano-directory-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/ano-file-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "Line Level",
                                href="/dash/analysis/ano-line-level/create?project_id={project_id}",
                            ),
                        ],
                        label="Anomaly Detection",
                        nav=True,
                    ),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/directory-level-visualisations/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/file-level-visualisations/create?project_id={project_id}",
                            ),
                        ],
                        label="High level Visualisations",
                        nav=True,
                    ),
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                "Directory Level",
                                href=f"/dash/analysis/distance-directory-level/create?project_id={project_id}",
                            ),
                            dbc.DropdownMenuItem(
                                "File Level",
                                href=f"/dash/analysis/distance-file-level/create?project_id={project_id}",
                            ),
                        ],
                        label="Log Distance",
                        nav=True,
                    ),
                ],
                id=nav_id,
                vertical=True,
                class_name="h5",
            ),
        ]
    )
