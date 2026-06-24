import pandas as pd
from statsmodels.tsa.stattools import coint


def test_cointegration(series_a: pd.Series, series_b: pd.Series) -> dict:
    """
    Run the Engle-Granger cointegration test on two price series.
    Returns the test statistic, p-value, and whether the pair is cointegrated (p < 0.05).
    A p-value below 0.05 means the spread is stationary and likely to mean-revert.
    """
    series_a = pd.to_numeric(series_a, errors="coerce").dropna()
    series_b = pd.to_numeric(series_b, errors="coerce").dropna()
    series_a, series_b = series_a.align(series_b, join="inner")

    if len(series_a) < 30:
        raise ValueError(f"Not enough overlapping data points ({len(series_a)}) — need at least 30. Try widening the date range.")

    test_stat, p_value, _ = coint(series_a, series_b)

    return {
        "test_stat": float(test_stat),
        "p_value": float(p_value),
        "is_cointegrated": bool(p_value < 0.05),
    }
