from datetime import datetime
import pandas as pd
from statsmodels.tsa.stattools import coint
from analysis.data_loader import load_pair_data
from analysis.screener import screen_sector, SECTOR_TICKERS

START = "2020-01-01"
END = datetime.today().strftime("%Y-%m-%d")
MIN_CORR = 0.60
MAX_P_VALUE = 0.05


def test_cointegration(ticker_a, ticker_b):
    try:
        df = load_pair_data(ticker_a, ticker_b, START, END, cache=True)
        series_a = pd.to_numeric(df[f"Close_{ticker_a}"].squeeze(), errors="coerce").dropna()
        series_b = pd.to_numeric(df[f"Close_{ticker_b}"].squeeze(), errors="coerce").dropna()
        series_a, series_b = series_a.align(series_b, join="inner")
        if len(series_a) < 30:
            return None
        _, p_value, _ = coint(series_a, series_b)
        return round(float(p_value), 4)
    except Exception as e:
        print(f"  [error] {ticker_a}/{ticker_b}: {e}")
        return None


all_candidates = []

for sector, tickers in SECTOR_TICKERS.items():
    print(f"Screening {sector} ({len(tickers)} tickers)")

    corr_pairs = screen_sector(tickers, START, END, min_corr=MIN_CORR)
    print(f"Found {len(corr_pairs)} correlated pairs, running cointegration")

    for pair in corr_pairs:
        a, b = pair["ticker_a"], pair["ticker_b"]
        print(f"  Testing {a}/{b} (corr={pair['correlation']:.3f})", end=" ", flush=True)
        p = test_cointegration(a, b)
        if p is None:
            print("skipped")
            continue
        status = "PASS" if p < MAX_P_VALUE else "FAIL"
        print(f"p={p:.4f} {status}")
        all_candidates.append({
            "ticker_a": a,
            "ticker_b": b,
            "sector": sector,
            "correlation": pair["correlation"],
            "p_value": p,
            "cointegrated": p < MAX_P_VALUE,
        })

validated = [c for c in all_candidates if c["cointegrated"]]
validated.sort(key=lambda x: x["p_value"])

print(f"VALIDATED PAIRS (p < {MAX_P_VALUE})")
print(f"{'Pair':<15} {'Sector':<15} {'Corr':>6} {'p-value':>8}")
for v in validated:
    pair_str = f"{v['ticker_a']}/{v['ticker_b']}"
    print(f"{pair_str:<15} {v['sector']:<15} {v['correlation']:>6.3f} {v['p_value']:>8.4f}")

print(f"\nTotal validated: {len(validated)} / {len(all_candidates)} tested")