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


def files_and_lines_count(df):
    files_and_lines = (
        df.group_by("run")
        .agg(
            [
                pl.len().alias("line_count"),
                pl.col("file_name").n_unique().alias("file_count"),
            ]
        )
        .sort("run")
    )

    return files_and_lines


def aggregate_run_level(df, item_list_col):
    df = (
        df.select("run", item_list_col)
        .explode(item_list_col)
        .group_by("run")
        .agg(pl.col(item_list_col))
    )

    return df
