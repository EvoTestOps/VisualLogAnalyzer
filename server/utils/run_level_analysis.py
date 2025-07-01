import polars as pl
from server.services.enhancer import Enhancer


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


def aggregate_run_level(df, item_list_col, mask_type=None):
    if df.get_column(item_list_col, default=None) is None:
        enhancer = Enhancer(df)
        df = enhancer.enhance_event(item_list_col, mask_type)

    col_dtype = df.select(pl.col(item_list_col)).dtypes[0]

    if isinstance(col_dtype, pl.List):
        df = df.select("run", item_list_col).explode(item_list_col)
    else:
        df = df.select("run", item_list_col)

    df = (df.group_by("run").agg(pl.col(item_list_col))).sort("run")

    return df


# https://github.com/EvoTestOps/LogDelta/blob/main/logdelta/log_analysis_functions.py
# Mika Mäntylä
def calculate_zscore_sum_anos(df, distance_columns: list[str]):
    import numpy as np
    from scipy.stats import zscore, rankdata

    """
    This function normalizes the distance measures in the DataFrame using Z-scores,
    sums the normalized values for each comparison run, and appends the zscore_sum
    as a new column to the DataFrame.

    Args:
    df (pl.DataFrame): DataFrame containing distance measures (e.g., kmeans_pred_ano_proba,
                       IF_pred_ano_proba, RM_pred_ano_proba, OOVD_pred_ano_proba).

    Returns:
    pl.DataFrame: Updated DataFrame with an additional 'zscore_sum' column.
    """
    # Define the columns to normalize
    if isinstance(df, pl.DataFrame):
        # distance_columns = [
        #     "kmeans_pred_ano_proba",
        #     "IF_pred_ano_proba",
        #     "RM_pred_ano_proba",
        #     "OOVD_pred_ano_proba",
        # ]
        # Replace None with np.nan for compatibility with numpy operations
        df = df.with_columns([pl.col(col).fill_nan(np.nan) for col in distance_columns])
        # Convert Polars DataFrame to a list of dictionaries
        results = df.to_dicts()
    elif isinstance(df, list):
        # distance_columns = ["cosine", "jaccard", "compression", "containment"]
        results = df
    else:
        raise ValueError(
            f"Error: Unsupported datatype: {type(df)}. Supported types are: pl.DataFrame and list"
        )

    # Create the distance matrix from the results, explicitly replacing None with np.nan
    distance_matrix = np.array(
        [
            [
                np.nan if result.get(col) is None else result[col]
                for col in distance_columns
            ]
            for result in results
        ]
    )

    # Normalize each distance column using z-scores, ignoring NaN values
    normalized_distances = np.apply_along_axis(
        lambda col: zscore(col, nan_policy="omit"), axis=0, arr=distance_matrix
    )

    # Sum the normalized distances for each comparison run
    zscore_sum = normalized_distances.sum(axis=1)

    # Compute ranks for each distance column, ignoring NaN values
    rank_matrix = np.apply_along_axis(
        lambda col: rankdata(col, nan_policy="omit"), axis=0, arr=distance_matrix
    )

    # Sum the ranks for each comparison run
    rank_sum = rank_matrix.sum(axis=1)

    # Add the z-score sum and rank sum to each result
    for idx, result in enumerate(results):
        result["zscore_sum"] = zscore_sum[idx]
        result["rank_sum"] = rank_sum[idx]

    # If the input was Polars Datafame convert the updated results back to a Polars DataFrame
    if isinstance(df, pl.DataFrame):
        return pl.DataFrame(results)
    elif isinstance(df, list):
        return results
    else:
        raise ValueError(
            f"Error: Unsupported datatype: {type(df)}. Supported types are: pl.DataFrame and list"
        )
