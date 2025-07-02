import polars as pl
from server.analysis.enhancer import Enhancer


def unique_terms_count_by_file(df, item_list_col):
    enhancer = Enhancer(df)
    df = enhancer.enhance_event(item_list_col)

    file_unique_terms = (
        df.select("seq_id", item_list_col)
        .group_by("seq_id")
        .agg(
            [
                pl.len().alias("line_count"),
                pl.col(item_list_col)
                .list.explode()
                .n_unique()
                .alias("unique_term_count"),
            ]
        )
    )

    return file_unique_terms.sort("seq_id")


def aggregate_file_level(df, item_list_col, mask_type=None):
    if df.get_column(item_list_col, default=None) is None:
        enhancer = Enhancer(df)
        df = enhancer.enhance_event(item_list_col, mask_type)

    col_dtype = df.select(pl.col(item_list_col)).dtypes[0]

    if isinstance(col_dtype, pl.List):
        df = df.select("seq_id", item_list_col).explode(item_list_col)
    else:
        df = df.select("seq_id", item_list_col)

    df = (df.group_by("seq_id").agg(pl.col(item_list_col))).sort("seq_id")

    return df


def aggregate_file_level_with_file_names(df, item_list_col):
    if df.get_column(item_list_col, default=None) is None:
        enhancer = Enhancer(df)
        df = enhancer.enhance_event(item_list_col)

    col_dtype = df.select(pl.col(item_list_col)).dtypes[0]

    if isinstance(col_dtype, pl.List):
        df = df.select("seq_id", "file_name", item_list_col).explode(item_list_col)
    else:
        df = df.select("seq_id", "file_name", item_list_col)

    df = (df.group_by(["seq_id", "file_name"]).agg(pl.col(item_list_col))).sort(
        "seq_id"
    )

    return df
