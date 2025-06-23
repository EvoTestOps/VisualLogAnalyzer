import polars as pl
from services.enhancer import Enhancer


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


def aggregate_file_level(df, item_list_col):
    if df.get_column(item_list_col, default=None) is None:
        enhancer = Enhancer(df)
        df = enhancer.enhance_event(item_list_col)

    df = (
        df.select("seq_id", item_list_col)
        .explode(item_list_col)
        .group_by("seq_id")
        .agg(pl.col(item_list_col))
    ).sort("seq_id")

    return df
