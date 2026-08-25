import polars as pl
import plotly.graph_objects as go

from dash_app.utils.grouping import GROUP_COLUMN

# Colors and shapes are combined, so the number of groups that stay apart is the
# count of colors times the count of shapes. The colors are picked from the
# published colour-blind safe palettes (Okabe & Ito, Paul Tol, IBM) as the five
# that stay furthest apart when simulated for protanopia, deuteranopia and
# tritanopia, while keeping enough contrast against both the light and the dark
# theme. The shape carries the difference for anyone who sees no color at all.
GROUP_COLORS = [
    "#33BBEE",  # blue
    "#E69F00",  # orange
    "#117733",  # green
    "#AA3377",  # magenta
    "#785EF0",  # violet
]

GROUP_SYMBOLS = [
    "circle",
    "square",
    "diamond",
    "triangle-up",
    "triangle-down",
    "cross",
    "x",
    "star",
    "pentagon",
    "hexagram",
]


def get_options(df) -> list[dict]:
    seq_ids = sorted(df["seq_id"].unique().to_list())
    return [{"label": seq_id, "value": seq_id} for seq_id in seq_ids]


def create_line_level_plot(
    df, selected_plot, theme="plotly_white", normalize_scores=True
):
    df = df.filter(pl.col("seq_id") == selected_plot)

    if df.get_column("line_number", default=None) is None:
        df = df.with_row_index()
        xaxis_title = "Index"
        x_column = "index"
    else:
        xaxis_title = "Line Number"
        x_column = "line_number"

    prediction_columns = [
        col
        for col in df.columns
        if "pred_ano_proba" in col and not col.startswith("moving_avg")
    ]
    moving_avg_columns = [col for col in df.columns if "moving_avg" in col]

    numeric_dtypes = pl.NUMERIC_DTYPES
    measure_groups = [
        [
            col
            for col in df.columns
            if "kmeans" in col and df.schema[col] in numeric_dtypes
        ],
        [col for col in df.columns if "if" in col and df.schema[col] in numeric_dtypes],
        [col for col in df.columns if "rm" in col and df.schema[col] in numeric_dtypes],
        [
            col
            for col in df.columns
            if "oovd" in col and df.schema[col] in numeric_dtypes
        ],
    ]

    if normalize_scores:
        for columns in measure_groups:
            if columns:
                df = _normalize_prediction_columns(df, columns)

    # polars documentation says that map_elements is slow.
    # Change if it becomes an issue.
    df = df.with_columns(
        [
            pl.col("m_message")
            .map_elements(_wrap_log, return_dtype=pl.String)
            .alias("m_message_wrapped")
        ]
    )

    directory_name = df["run"][0]
    file_name = df["file_name"][0]

    fig = go.Figure()

    for col in prediction_columns + moving_avg_columns:
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[col],
                mode="markers",
                name=col,
                customdata=df["m_message_wrapped"],
                hovertemplate=f"{xaxis_title}: %{{x}}<br>Score ({col}): %{{y}}<br>Log: %{{customdata}}<extra></extra>",
                marker=dict(symbol="x", size=4),
            )
        )

    title = (
        f"Normalized Anomaly Score<br>File: {file_name}<br>Directory: {directory_name}"
        if normalize_scores
        else f"Anomaly Score<br>File: {file_name}<br>Directory: {directory_name}"
    )
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title="Anomaly Score (0 - 1)" if normalize_scores else "Anomaly Score",
        template=theme,
    )

    if not normalize_scores:
        fig.update_yaxes(type="log")

    return fig


def create_line_level_plot_minimal(
    df, selected_plot, plot_columns, theme="plotly_white"
):
    df = df.filter(pl.col("seq_id") == selected_plot)

    if df.get_column("line_number", default=None) is None:
        df = df.with_row_index()
        x_column = "index"
    else:
        x_column = "line_number"

    numeric_dtypes = pl.NUMERIC_DTYPES
    measure_groups = [
        [
            col
            for col in df.columns
            if "kmeans" in col and df.schema[col] in numeric_dtypes
        ],
        [col for col in df.columns if "if" in col and df.schema[col] in numeric_dtypes],
        [col for col in df.columns if "rm" in col and df.schema[col] in numeric_dtypes],
        [
            col
            for col in df.columns
            if "oovd" in col and df.schema[col] in numeric_dtypes
        ],
    ]

    for columns in measure_groups:
        if columns:
            df = _normalize_prediction_columns(df, columns)

    fig = go.Figure()
    for col in plot_columns:
        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[col],
                mode="markers",
                marker=dict(symbol="x", size=4),
                showlegend=False,
            )
        )

    directory_name = df["run"][0]
    file_name = df["file_name"][0]

    fig.update_layout(
        title=f"{file_name}<br>{directory_name}",
        margin=dict(l=20, r=20, t=50, b=20),
        template=theme,
        showlegend=False,
    )

    return fig


def create_unique_term_count_plot(df, theme="plotly_white"):
    fig = go.Figure()

    _add_marker_traces(
        fig,
        _split_by_group(df, "Runs"),
        x_column="unique_term_count",
        y_column="line_count",
        text_column="run",
        hovertemplate="Run: %{text}<br>Unique terms: %{x}<br>Lines:%{y}<extra></extra>",
    )

    fig.update_layout(
        title="Unique term count by run",
        xaxis_title="Unique terms",
        yaxis_title="Lines",
        template=theme,
    )

    fig.update_yaxes(type="log")

    return fig


def create_unique_term_count_plot_by_file(
    df, color_by_directory=False, theme="plotly_white"
):
    fig = go.Figure()

    if GROUP_COLUMN in df.columns:
        frames = _split_by_group(df, "Files")
    elif color_by_directory:
        frames = _split_by_directory(df)
    else:
        frames = [("Files", df)]

    _add_marker_traces(
        fig,
        frames,
        x_column="unique_term_count",
        y_column="line_count",
        text_column="seq_id",
        hovertemplate="File: %{text}<br>Unique terms: %{x}<br>Lines:%{y}<extra></extra>",
    )

    fig.update_layout(
        title="Unique term count by file",
        xaxis_title="Unique terms",
        yaxis_title="Lines",
        template=theme,
    )

    fig.update_yaxes(type="log")

    return fig


def create_files_count_plot(df, theme="plotly_white"):
    fig = go.Figure()

    _add_marker_traces(
        fig,
        _split_by_group(df, "Runs"),
        x_column="file_count",
        y_column="line_count",
        text_column="run",
        hovertemplate="Run: %{text}<br>Files: %{x}<br>Lines:%{y}<extra></extra>",
    )

    fig.update_layout(
        title="File count by run",
        xaxis_title="Files",
        yaxis_title="Lines",
        template=theme,
    )

    fig.update_yaxes(type="log")

    return fig


def create_umap_plot(df, group_col, color_by_directory=False, theme="plotly_white"):
    fig = go.Figure()

    if GROUP_COLUMN in df.columns:
        frames = _split_by_group(df, None)
    elif group_col == "seq_id" and color_by_directory:
        frames = _split_by_directory(df)
    else:
        frames = [(None, df)]

    _add_marker_traces(
        fig,
        frames,
        x_column="UMAP1",
        y_column="UMAP2",
        text_column=group_col,
        hovertemplate=f"{group_col}: %{{text}}<br>UMAP1: %{{x}}<br>UMAP2:%{{y}}<extra></extra>",
        size=6,
    )

    fig.update_layout(
        title="UMAP comparison",
        xaxis_title="UMAP1",
        yaxis_title="UMAP2",
        template=theme,
    )

    return fig


def _add_marker_traces(
    fig, frames, x_column, y_column, text_column, hovertemplate, size=8
):
    """Draw one marker trace per frame, each with its own color and shape."""
    for index, (name, frame) in enumerate(frames):
        fig.add_trace(
            go.Scatter(
                x=frame[x_column],
                y=frame[y_column],
                mode="markers",
                text=frame[text_column],
                hovertemplate=hovertemplate,
                name=name,
                marker=_group_marker(index, size),
            )
        )


def _group_marker(index, size):
    # The colors are cycled through first and the shape changes once they run
    # out, so every combination is used before any of them comes back.
    return dict(
        color=GROUP_COLORS[index % len(GROUP_COLORS)],
        symbol=GROUP_SYMBOLS[(index // len(GROUP_COLORS)) % len(GROUP_SYMBOLS)],
        size=size,
        # A neutral outline keeps the palest markers visible in both themes.
        line=dict(width=1, color="rgba(128, 128, 128, 0.8)"),
    )


def _split_by_group(df, default_name):
    """Frames to draw as separate traces, one per group when the data is grouped."""
    if GROUP_COLUMN not in df.columns:
        return [(default_name, df)]

    return [
        (group, df.filter(pl.col(GROUP_COLUMN) == group))
        for group in sorted(df[GROUP_COLUMN].unique())
    ]


def _split_by_directory(df):
    return [
        (f"Directory: {run}", df.filter(pl.col("run") == run))
        for run in sorted(df["run"].unique())
    ]


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
