import polars as pl


def filter_runs(df, runs: list[str], include=True):
    df = (
        df.filter(pl.col("run").is_in(runs))
        if include
        else df.filter(~pl.col("run").is_in(runs))
    )
    return df


def filter_files(df, files: list[str], column: str = "orig_file_name", include=True):
    df = (
        df.filter(pl.col(column).is_in(files))
        if include
        else df.filter(~pl.col(column).is_in(files))
    )
    return df


def get_prediction_cols(df) -> list[str]:
    return [col for col in df.columns if "pred_ano_proba" in col]
