import pytest
import pandas as pd
import numpy as np
from analysis.spread import (
    estimate_hedge_ratio,
    estimate_rolling_hedge_ratio,
    calculate_spread_metrics,
)


def make_pair_df(prices_a, prices_b):
    """Helper to build a DataFrame in the format load_pair_data returns."""
    dates = pd.date_range("2020-01-01", periods=len(prices_a), freq="B")
    return pd.DataFrame({
        "Date": dates,
        "Close_A": prices_a,
        "Close_B": prices_b,
    })


def test_estimate_hedge_ratio_perfect_relationship():
    # B = 2 * A exactly, so beta should be ~0.5
    a = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    b = pd.Series([20.0, 40.0, 60.0, 80.0, 100.0])
    beta = estimate_hedge_ratio(a, b)
    assert abs(beta - 0.5) < 0.01


def test_estimate_hedge_ratio_not_one():
    # Verify it doesn't just return 1.0
    a = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0])
    b = pd.Series([50.0, 50.5, 51.0, 51.5, 52.0])
    beta = estimate_hedge_ratio(a, b)
    assert beta != 1.0


def test_rolling_hedge_ratio_length():
    a = pd.Series(range(1, 101), dtype=float)
    b = pd.Series(range(2, 202, 2), dtype=float)
    rolling = estimate_rolling_hedge_ratio(a, b, window=60)
    assert len(rolling) == len(a)


def test_rolling_hedge_ratio_nan_before_window():
    a = pd.Series(range(1, 101), dtype=float)
    b = pd.Series(range(2, 202, 2), dtype=float)
    rolling = estimate_rolling_hedge_ratio(a, b, window=60)
    # first 59 values should be NaN since window hasn't filled yet
    assert rolling.iloc[:59].isna().all()
    assert not pd.isna(rolling.iloc[59])


def test_calculate_spread_metrics_hedge_ratio_in_output():
    df = make_pair_df(
        [100, 101, 102, 103, 104],
        [50,  51,  52,  53,  54],
    )
    result_df, metrics = calculate_spread_metrics(df, "A", "B", spread_type="difference")
    assert "hedge_ratio" in metrics
    assert isinstance(metrics["hedge_ratio"], float)
    assert metrics["hedge_ratio"] > 0
    assert "hedge_ratio" in result_df.columns


def test_calculate_spread_metrics_log_ratio_with_hedge_ratio():
    df = make_pair_df(
        [100, 101, 102, 103, 104],
        [50,  51,  52,  53,  54],
    )
    result_df, metrics = calculate_spread_metrics(df, "A", "B", spread_type="log_ratio")
    assert "hedge_ratio" in metrics
    assert not result_df["spread"].isna().all()