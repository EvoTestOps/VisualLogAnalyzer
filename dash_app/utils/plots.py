import polars as pl
import plotly.graph_objects as go


def get_options(df):
    seq_ids = sorted(df["seq_id"].unique().to_list())
    return [{"label": seq_id, "value": seq_id} for seq_id in seq_ids]


def create_plot(df, selected_plot):
    prediction_columns = [col for col in df.columns if "pred_ano_proba" in col]
    df = df.filter(pl.col("seq_id") == selected_plot).with_row_index()

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
