import dash_bootstrap_components as dbc
from dash_app.components.form_inputs import (
    log_format_input,
    directory_input,
    detectors_input,
    enhancement_input,
    sequence_input,
    test_frac_input,
    submit_button,
    train_data_input,
    test_data_input,
)


# Currently hardcoded id values
def labeled_form():
    submit_btn = submit_button("submit", "Analyze")

    form = dbc.Form(
        [
            dbc.Row(
                [log_format_input("log_format"), directory_input("directory")],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_input("detectors"),
                    enhancement_input("enhancement"),
                    sequence_input("sequence"),
                ],
                class_name="mb-3",
            ),
            test_frac_input("test_frac"),
            dbc.Row(dbc.Col(submit_btn, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form


def test_train_form():
    submit_btn_tr = submit_button("submit_tr", "Analyze")

    form_tr = dbc.Form(
        [
            dbc.Row(
                [
                    log_format_input("log_format_tr"),
                    train_data_input("train_data_tr"),
                    test_data_input("test_data_tr"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(
                [
                    detectors_input("detectors_tr"),
                    enhancement_input("enhancement_tr"),
                    sequence_input("sequence_tr"),
                ],
                class_name="mb-3",
            ),
            dbc.Row(dbc.Col(submit_btn_tr, class_name="text-end")),
        ],
        class_name="border border-primary-subtle border-2 p-3",
    )

    return form_tr
