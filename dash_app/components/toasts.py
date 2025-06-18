import dash_bootstrap_components as dbc


def error_toast(id):
    return dbc.Toast(
        id=id,
        header="Error",
        icon="danger",
        is_open=False,
        dismissable=True,
        duration=15000,
        style={"position": "fixed", "top": 40, "right": 10, "width": 400},
    )


def success_toast(id):
    return dbc.Toast(
        id=id,
        header="Success",
        icon="success",
        is_open=False,
        dismissable=True,
        duration=10000,
        style={"position": "fixed", "top": 40, "right": 10, "width": 400},
    )
