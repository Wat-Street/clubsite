import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def simple_pair_df():
    """5-row DataFrame mimicking load_pair_data output."""
    return pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=5, freq="B"),
        "Close_AAPL": [100.0, 110.0, 105.0, 115.0, 120.0],
        "Close_MSFT": [50.0, 55.0, 52.0, 58.0, 60.0],
    })


@pytest.fixture
def constant_series():
    return pd.Series([5.0, 5.0, 5.0, 5.0, 5.0])


@pytest.fixture
def textbook_series():
    """Mean=5.0, std(ddof=1)=2.13809."""
    return pd.Series([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])


@pytest.fixture
def leader_follower_pair():
    """b[t] = a[t-1] exactly."""
    a = pd.Series([1.0, 3.0, 2.0, 5.0, 4.0, 1.0, 3.0, 6.0])
    b = pd.Series([0.0, 1.0, 3.0, 2.0, 5.0, 4.0, 1.0, 3.0])
    return a, b
