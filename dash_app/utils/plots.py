import polars as pl
import plotly.graph_objects as go


def get_options(df):
    seq_ids = sorted(df["seq_id"].unique().to_list())
    return [{"label": seq_id, "value": seq_id} for seq_id in seq_ids]


def create_plot(df, selected_plot):
    prediction_columns = [col for col in df.columns if "pred_ano_proba" in col]
    df = df.filter(pl.col("seq_id") == selected_plot).with_row_index()

    df = _normalize_prediction_columns(df, prediction_columns)

    # polars documentation says that map_elements is slow.
    # Change if it becomes an issue.
    df = df.with_columns(
        [
            pl.col("m_message")
            .map_elements(_wrap_log, return_dtype=pl.String)
            .alias("m_message_wrapped")
        ]
    )

    fig = go.Figure()

    for col in prediction_columns:
        fig.add_trace(
            go.Scatter(
                x=df["index"],
                y=df[col],
                mode="markers",
                name=col,
                customdata=df["m_message_wrapped"],
                hovertemplate="Index: %{x}<br>Score: %{y}<br>Log: %{customdata}<extra></extra>",
            )
        )

    fig.update_layout(
        title=selected_plot, xaxis_title="Index", yaxis_title="Anomaly Score"
    )

    return fig


def _wrap_log(text, width=80):
    return "<br>".join([text[i : i + width] for i in range(0, len(text), width)])


# Edited version of _normalize_measure_columns from LogDelta by Mika Mäntylä
# https://github.com/EvoTestOps/LogDelta/blob/main/logdelta/log_analysis_functions.py
def _normalize_prediction_columns(df, columns):

    filled = df.select(columns).with_columns(pl.all().fill_null(pl.all().median()))

    measure_min = filled.min().to_numpy().min()
    measure_max = filled.max().to_numpy().max()

    if measure_min == measure_max:
        return df

    normalized = [
        ((pl.col(col) - measure_min) / measure_max - measure_min).alias(col)
        for col in columns
    ]

    return df.with_columns(normalized)
