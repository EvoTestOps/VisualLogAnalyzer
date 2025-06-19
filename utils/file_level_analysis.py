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
