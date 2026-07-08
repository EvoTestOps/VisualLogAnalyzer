import polars as pl


def calculate_moving_average_by_columns(
    df: pl.DataFrame, window_size: int, columns: list[str]
) -> pl.DataFrame:

    if df.height == 0:
        return pl.DataFrame({f"moving_avg_{window_size}_{col}": [] for col in columns})

    moving_avg_exprs = [
        pl.col(col).rolling_mean(window_size).alias(f"moving_avg_{window_size}_{col}")
        for col in columns
    ]
    return df.select(moving_avg_exprs)
