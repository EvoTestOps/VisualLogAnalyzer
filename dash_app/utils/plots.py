import polars as pl
import plotly.graph_objects as go


def get_options(df):
    seq_ids = sorted(df["seq_id"].unique().to_list())
    return [{"label": seq_id, "value": seq_id} for seq_id in seq_ids]


def create_line_level_plot(df, selected_plot, theme="plotly_white"):
    prediction_columns = [col for col in df.columns if "pred_ano_proba" in col]

    df = df.filter(pl.col("seq_id") == selected_plot)
    if df.get_column("line_number", default=None) is None:
        df = df.with_row_index()
        xaxis_title = "Index"
        x_column = "index"
    else:
        xaxis_title = "Line Number"
        x_column = "line_number"

    for col in prediction_columns:
        df = _normalize_prediction_columns(df, [col])

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
                x=df[x_column],
                y=df[col],
                mode="markers",
                name=col,
                customdata=df["m_message_wrapped"],
                hovertemplate=f"{xaxis_title}: %{{x}}<br>Score ({col}): %{{y}}<br>Log: %{{customdata}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=selected_plot,
        xaxis_title=xaxis_title,
        yaxis_title="Anomaly Score (0 - 1)",
        template=theme,
    )

    return fig


def create_unique_term_count_plot(df, theme="plotly_white"):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["unique_term_count"],
            y=df["line_count"],
            mode="markers",
            text=df["run"],
            hovertemplate="Run: %{text}<br>Unique terms: %{x}<br>Lines:%{y}<extra></extra>",
            name="Runs",
        )
    )

    fig.update_layout(
        title="Unique term count by run",
        xaxis_title="Unique terms",
        yaxis_title="Lines",
        template=theme,
    )

    return fig


def create_unique_term_count_plot_by_file(df, theme="plotly_white"):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["unique_term_count"],
            y=df["line_count"],
            mode="markers",
            text=df["seq_id"],
            hovertemplate="File: %{text}<br>Unique terms: %{x}<br>Lines:%{y}<extra></extra>",
            name="Files",
        )
    )

    fig.update_layout(
        title="Unique term count by file",
        xaxis_title="Unique terms",
        yaxis_title="Lines",
        template=theme,
    )

    return fig


def create_files_count_plot(df, theme="plotly_white"):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["file_count"],
            y=df["line_count"],
            mode="markers",
            text=df["run"],
            hovertemplate="Run: %{text}<br>Files: %{x}<br>Lines:%{y}<extra></extra>",
            name="Runs",
        )
    )

    fig.update_layout(
        title="File count by run",
        xaxis_title="Files",
        yaxis_title="Lines",
        template=theme,
    )

    return fig


def create_umap_plot(df, group_col, theme="plotly_white"):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["UMAP1"],
            y=df["UMAP2"],
            mode="markers",
            text=df[group_col],
            hovertemplate=f"{group_col}: %{{text}}<br>UMAP1: %{{x}}<br>UMAP2:%{{y}}<extra></extra>",
        )
    )

    fig.update_layout(
        title="UMAP comparison",
        xaxis_title="UMAP1",
        yaxis_title="UMAP2",
        template=theme,
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
        ((pl.col(col) - measure_min) / (measure_max - measure_min)).alias(col)
        for col in columns
    ]

    return df.with_columns(normalized)
