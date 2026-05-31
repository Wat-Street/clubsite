"""
correlation-api/analysis/screener.py

Screens a sector's tickers for correlated pairs above a minimum threshold.
Uses log returns (not raw prices) for correlation — more stationary and
comparable across different price scales.

Step 1 of pair discovery. Cointegration filter (Khush's) is step 2.
"""

import itertools
import pandas as pd
import numpy as np
from analysis.data_loader import get_stock_data

# ---------------------------------------------------------------------------
# Sector universes — hardcoded to start, extend as follow-up tasks land
# ---------------------------------------------------------------------------

SECTOR_TICKERS: dict[str, list[str]] = {
    "technology": [
        "AAPL", "MSFT", "GOOGL", "META", "NVDA",
        "AMD",  "INTC", "AVGO", "QCOM", "TXN",
        "ORCL", "CRM",  "ADBE", "NOW",  "SNOW",
    ],
}


def _load_returns(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """
    Fetch closing prices for all tickers and compute daily log returns.

    Returns a DataFrame indexed by Date with one column per ticker.
    Tickers that fail to load are silently dropped with a warning so a
    single bad symbol doesn't abort the whole screen.
    """
    frames: dict[str, pd.Series] = {}

    for ticker in tickers:
        try:
            df = get_stock_data(ticker, start, end, cache=True)
            prices = pd.to_numeric(df.set_index("Date")["Close"], errors="coerce").dropna()
            if prices.empty:
                print(f"[screener] Warning: no price data for {ticker}, skipping.")
                continue
            # Log returns: ln(P_t / P_{t-1})
            log_ret = np.log(prices / prices.shift(1)).dropna()
            frames[ticker] = log_ret
        except Exception as exc:
            print(f"[screener] Warning: could not load {ticker} — {exc}")

    if not frames:
        return pd.DataFrame()

    # Inner join so every column has the same date range
    returns = pd.DataFrame(frames).dropna()
    return returns


def screen_sector(
    tickers: list[str],
    start: str,
    end: str,
    min_corr: float = 0.85,
) -> list[dict]:
    """
    Find all pairs in `tickers` whose log-return Pearson correlation
    is at or above `min_corr` over [start, end].

    Args:
        tickers:  List of ticker symbols to screen.
        start:    Start date string, e.g. "2024-01-01".
        end:      End date string,   e.g. "2025-01-01".
        min_corr: Minimum absolute correlation to include (default 0.85).

    Returns:
        List of dicts sorted descending by correlation:
            [{"ticker_a": str, "ticker_b": str, "correlation": float}, ...]
    """
    if len(tickers) < 2:
        raise ValueError("Need at least 2 tickers to screen.")
    if not (0.0 <= min_corr <= 1.0):
        raise ValueError(f"min_corr must be in [0, 1], got {min_corr}.")

    print(f"[screener] Loading returns for {len(tickers)} tickers ({start} → {end})...")
    returns = _load_returns(tickers, start, end)

    if returns.shape[1] < 2:
        return []

    print(f"[screener] Computing pairwise correlations across {returns.shape[1]} tickers "
          f"({returns.shape[0]} trading days)...")

    corr_matrix = returns.corr(method="pearson")
    loaded_tickers = list(returns.columns)

    results: list[dict] = []
    for ticker_a, ticker_b in itertools.combinations(loaded_tickers, 2):
        corr = float(corr_matrix.loc[ticker_a, ticker_b])
        if np.isnan(corr):
            continue
        if abs(corr) >= min_corr:
            results.append({
                "ticker_a":    ticker_a,
                "ticker_b":    ticker_b,
                "correlation": round(corr, 6),
            })

    results.sort(key=lambda x: x["correlation"], reverse=True)
    print(f"[screener] Found {len(results)} pairs with |corr| ≥ {min_corr}.")
    return results
