from dash import clientside_callback, Output, Input


def color_switch_callback():
    clientside_callback(
        """
        (switchOn) => {
        document.documentElement.setAttribute("data-bs-theme", switchOn ? "light" : "dark");
        return window.dash_clientside.no_update
        }
        """,
        Output("switch", "id"),
        Input("switch", "value"),
    )
