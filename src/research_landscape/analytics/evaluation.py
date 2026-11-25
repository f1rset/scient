"""Retrospective evaluation guards shared by future backtest implementations."""


def evaluation_windows(cutoffs, horizons, complete_through):
    return [
        (cutoff, horizon) for cutoff in cutoffs for horizon in horizons
        if horizon > 0 and cutoff + horizon <= complete_through
    ]


def enforce_cutoff(feature_year, cutoff):
    if feature_year > cutoff:
        raise ValueError("Feature observation exceeds the historical cutoff")


def feature_rows(frame, cutoff, year_column="publication_year"):
    from pyspark.sql import functions as f

    return frame.where(f.col(year_column) <= cutoff)


def rank_evaluation(*args, **kwargs):
    # TODO: Implement tie-aware Spearman, precision@K and overlap against baselines.
    raise NotImplementedError("Retrospective rank evaluation is pending")
