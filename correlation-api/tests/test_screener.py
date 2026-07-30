import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from analysis.screener import screen_sector, _load_returns

# Minimal mock price data — 5 days, 2 tickers moving together
def make_mock_df(ticker, prices):
    return pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "Close": prices,
        "Ticker": ticker
    })

@patch("analysis.screener.get_stock_data")
def test_screen_sector_returns_correlated_pair(mock_get):
    # AAPL and MSFT move identically — should have correlation ~1.0
    mock_get.side_effect = lambda ticker, start, end, cache: (
        make_mock_df("AAPL", [100, 101, 102, 103, 104]) if ticker == "AAPL"
        else make_mock_df("MSFT", [200, 202, 204, 206, 208])
    )
    results = screen_sector(["AAPL", "MSFT"], "2024-01-01", "2024-01-05", min_corr=0.90)
    assert len(results) == 1
    assert results[0]["ticker_a"] == "AAPL"
    assert results[0]["ticker_b"] == "MSFT"
    assert results[0]["correlation"] >= 0.90

@patch("analysis.screener.get_stock_data")
def test_screen_sector_filters_low_correlation(mock_get):
    # AAPL trends up, MSFT moves randomly — low positive correlation, should be excluded
    mock_get.side_effect = lambda ticker, start, end, cache: (
        make_mock_df("AAPL", [100, 101, 102, 103, 104]) if ticker == "AAPL"
        else make_mock_df("MSFT", [200, 210, 195, 215, 200])
    )
    results = screen_sector(["AAPL", "MSFT"], "2024-01-01", "2024-01-05", min_corr=0.85)
    assert len(results) == 0

@patch("analysis.screener.get_stock_data")
def test_screen_sector_sorted_descending(mock_get):
    # Three tickers — verify output is sorted highest correlation first
    mock_get.side_effect = lambda ticker, start, end, cache: {
        "AAPL": make_mock_df("AAPL", [100, 101, 102, 103, 104]),
        "MSFT": make_mock_df("MSFT", [200, 202, 204, 206, 208]),
        "GOOG": make_mock_df("GOOG", [300, 301, 303, 302, 304]),
    }[ticker]
    results = screen_sector(["AAPL", "MSFT", "GOOG"], "2024-01-01", "2024-01-05", min_corr=0.50)
    correlations = [r["correlation"] for r in results]
    assert correlations == sorted(correlations, reverse=True)

def test_screen_sector_raises_on_too_few_tickers():
    with pytest.raises(ValueError):
        screen_sector(["AAPL"], "2024-01-01", "2024-01-05")

def test_screen_sector_raises_on_invalid_min_corr():
    with pytest.raises(ValueError):
        screen_sector(["AAPL", "MSFT"], "2024-01-01", "2024-01-05", min_corr=1.5)