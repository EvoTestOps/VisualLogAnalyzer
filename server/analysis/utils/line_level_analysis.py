import polars as pl


def calculate_moving_average_by_columns(
    df: pl.DataFrame, window_size: int, columns: list[str]
) -> pl.DataFrame:
    df_moving_avg = pl.DataFrame()
    for column in columns:
        df_moving_avg = df_moving_avg.hstack(
            df.select(
                pl.col(column)
                .rolling_mean(window_size)
                .alias(f"moving_avg_{window_size}_{column}")
            )
        )

    return df_moving_avg
