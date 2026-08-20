import polars as pl

GROUP_COLUMN = "group"
SEPARATOR = "_"


def get_group_source_column(df):
    """The column naming the points of a plot.

    File level results identify a point by seq_id, which is the directory and
    the file name, while directory level results only have the directory name.
    """
    return "seq_id" if "seq_id" in df.columns else "run"


def add_group_column(df, group_by_indices, source_column=None, separator=SEPARATOR):
    """Label every row by the chosen parts of its name.

    Works like LogDelta's group_by_indices setting: the name is split on the
    separator and the parts at the given indices, in the order they were given,
    make up the label. Negative indices count from the end of the name, so that
    the last part can be picked no matter how long the name is. A name that has
    none of those parts is used as is.
    """
    source_column = source_column or get_group_source_column(df)

    label = (
        pl.col(source_column)
        .str.split(separator)
        .list.gather(group_by_indices, null_on_oob=True)
        .list.drop_nulls()
        .list.join(separator)
    )

    return df.with_columns(
        pl.when(label.str.len_chars() > 0)
        .then(label)
        .otherwise(pl.col(source_column))
        .alias(GROUP_COLUMN)
    )


def get_group_by_options(
    df, source_column=None, separator=SEPARATOR, max_values_shown=4
):
    """Dropdown options for the name parts the results can be grouped by.

    Every option lists the values found at that position, so that the part to
    group by can be picked without knowing the naming convention beforehand.
    Names that are not all of the same length also get options counted from the
    end, where the parts of such names line up.
    """
    source_column = source_column or get_group_source_column(df)
    if source_column not in df.columns:
        return []

    parts = df[source_column].str.split(separator)
    shortest = parts.list.len().min() or 0
    longest = parts.list.len().max() or 0

    indices = list(range(longest))
    if shortest != longest:
        indices += [-position for position in range(1, longest + 1)]

    options = []
    for index in indices:
        values = sorted(
            set(parts.list.get(index, null_on_oob=True).drop_nulls().to_list())
        )
        if not values:
            continue

        label = _part_label(index, shortest, longest)
        options.append(
            {
                "label": f"{label}: {_format_values(values, max_values_shown)}",
                "value": index,
            }
        )

    return options


def _part_label(index, shortest, longest):
    if index < 0:
        return f"Part {index} (from end)"

    if index == longest - 1 and shortest == longest:
        return f"Part {index} (last)"

    return f"Part {index}"


def _format_values(values, max_values_shown, max_value_length=24):
    shown = ", ".join(
        value if len(value) <= max_value_length else f"{value[:max_value_length]}..."
        for value in values[:max_values_shown]
    )
    if len(values) > max_values_shown:
        shown = f"{shown}, ... ({len(values)} values)"

    return shown
