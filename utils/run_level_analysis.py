import polars as pl
from services.enhancer import Enhancer


def unique_terms_count_by_run(df, item_list_col):
    enhancer = Enhancer(df)
    df = enhancer.enhance_event(item_list_col)

    run_unique_terms = (
        df.select("run", item_list_col)
        .group_by("run")
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

    return run_unique_terms.sort("run")
