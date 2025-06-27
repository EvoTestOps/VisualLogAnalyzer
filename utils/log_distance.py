import polars as pl
from loglead.anomaly_detection import LogDistance
from utils.run_level_analysis import calculate_zscore_sum_anos


def measure_distances(
    df,
    item_list_col,
    target_run,
    vectorizer,
    run_column="run",
    comparison_runs=None,
):
    comparison_run_names = (
        df.filter(
            (pl.col(run_column) != target_run)
            & (
                pl.col(run_column).is_in(comparison_runs)
                if comparison_runs not in (None, [])
                else True
            )
        )
        .select(run_column)
        .unique()
        .to_series()
        .to_list()
    )

    if len(comparison_run_names) == 0:
        raise ValueError("No comparison runs found.")

    df_target = df.filter(pl.col(run_column) == target_run)

    distances = []
    for comparison_run in sorted(comparison_run_names):
        df_comparison = df.filter(pl.col(run_column) == comparison_run)
        distances.append(
            _measure_distance(
                df_target,
                df_comparison,
                target_run,
                comparison_run,
                item_list_col,
                vectorizer,
            )
        )

    distance_columns = ["cosine", "jaccard", "compression", "containment"]
    distances = calculate_zscore_sum_anos(distances, distance_columns)

    return pl.DataFrame(distances)


def _measure_distance(
    df_target, df_comparison, target_name, comparison_name, item_list_col, vectorizer
):
    distance = LogDistance(
        df_target, df_comparison, item_list_col, vectorizer=vectorizer
    )

    cosine = distance.cosine()
    jaccard = distance.jaccard()
    compression = distance.compression()
    containment = distance.containment()

    result_row = {
        "target_run": target_name,
        "comparison_run": comparison_name,
        "target_lines": distance.size1,
        "comparison_lines": distance.size2,
        "cosine": cosine,
        "jaccard": jaccard,
        "compression": compression,
        "containment": containment,
    }

    return result_row
