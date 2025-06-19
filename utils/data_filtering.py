import polars as pl


def filter_runs(df, runs: list[str], include=True):
    df = (
        df.filter(pl.col("run").is_in(runs))
        if include
        else df.filter(~pl.col("run").is_in(runs))
    )
    return df


def filter_files(df, file_seq_ids: list[str], include=True):
    df = (
        df.filter(pl.col("seq_id").is_in(file_seq_ids))
        if include
        else df.filter(~pl.col("seq_id").is_in(file_seq_ids))
    )
    return df
