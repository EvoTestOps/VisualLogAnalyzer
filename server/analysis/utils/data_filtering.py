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


def get_file_name_by_orig_file_name(df, target: str) -> str:
    df_filtered = df.filter(pl.col("orig_file_name") == target)
    if not df_filtered.is_empty():
        return df_filtered.select("file_name")[0].item()
    else:
        raise ValueError(f"No file name found with target {target}")


def get_prediction_cols(df) -> list[str]:
    return [col for col in df.columns if "pred_ano_proba" in col]
