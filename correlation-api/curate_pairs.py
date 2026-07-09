from datetime import datetime
import pandas as pd
from statsmodels.tsa.stattools import coint
from analysis.data_loader import load_pair_data
from analysis.screener import screen_sector, SECTOR_TICKERS

START = "2020-01-01"
END = datetime.today().strftime("%Y-%m-%d")
MIN_CORR = 0.60
MAX_P_VALUE = 0.05

# Step 1 — existing 14 pairs to validate first
EXISTING_PAIRS = [
    ("MSFT", "GOOGL", "Technology"),
    ("AMD",  "NVDA",  "Technology"),
    ("CVS",  "JNJ",   "Healthcare"),
    ("PFE",  "MRK",   "Healthcare"),
    ("CL",   "KMB",   "Consumer"),
    ("KO",   "PEP",   "Consumer"),
    ("COST", "BJ",    "Consumer"),
    ("GE",   "BA",    "Industrials"),
    ("V",    "MA",    "Financials"),
    ("MS",   "GS",    "Financials"),
    ("JPM",  "BAC",   "Financials"),
    ("XOM",  "CVX",   "Energy"),
    ("T",    "VZ",    "Telecom"),
    ("WMT",  "TGT",   "Retail"),
]


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


# -----------------------------------------------------------------------
# Step 1 — run cointegration on existing 14 pairs, drop ones with p > 0.05
# -----------------------------------------------------------------------
print("STEP 1 — Validating existing 14 pairs")

kept = []
cut = []

for ticker_a, ticker_b, sector in EXISTING_PAIRS:
    print(f"  Testing {ticker_a}/{ticker_b}", end=" ", flush=True)
    p = test_cointegration(ticker_a, ticker_b)
    if p is None:
        print("skipped")
        continue
    status = "KEEP" if p < MAX_P_VALUE else "CUT"
    print(f"p={p:.4f} {status}")
    entry = {"ticker_a": ticker_a, "ticker_b": ticker_b, "sector": sector, "p_value": p}
    if p < MAX_P_VALUE:
        kept.append(entry)
    else:
        cut.append(entry)

print(f"\nKept: {len(kept)} / Cut: {len(cut)}")

# -----------------------------------------------------------------------
# Step 2 — run screener across sectors, cointegration test on candidates
# -----------------------------------------------------------------------
print("STEP 2 — Screener across sectors for new candidates")

screener_validated = []
existing_pair_keys = {(a, b) for a, b, _ in EXISTING_PAIRS} | {(b, a) for a, b, _ in EXISTING_PAIRS}

for sector, tickers in SECTOR_TICKERS.items():
    corr_pairs = screen_sector(tickers, START, END, min_corr=MIN_CORR)
    print(f"Found {len(corr_pairs)} correlated pairs")

    for pair in corr_pairs:
        a, b = pair["ticker_a"], pair["ticker_b"]

        # skip if already in existing pairs
        if (a, b) in existing_pair_keys:
            continue

        print(f"  Testing {a}/{b} (corr={pair['correlation']:.3f})", end=" ", flush=True)
        p = test_cointegration(a, b)
        if p is None:
            print("skipped")
            continue
        status = "PASS" if p < MAX_P_VALUE else "FAIL"
        print(f"p={p:.4f} {status}")
        if p < MAX_P_VALUE:
            screener_validated.append({
                "ticker_a": a,
                "ticker_b": b,
                "sector": sector,
                "correlation": pair["correlation"],
                "p_value": p,
            })

# -----------------------------------------------------------------------
# Step 3 — combine and de-dupe
# -----------------------------------------------------------------------
all_validated = kept + screener_validated

# de-dupe by pair key
seen = set()
final = []
for v in all_validated:
    key = tuple(sorted([v["ticker_a"], v["ticker_b"]]))
    if key not in seen:
        seen.add(key)
        final.append(v)

final.sort(key=lambda x: x["p_value"])

print(f"FINAL VALIDATED PAIRS (p < {MAX_P_VALUE}, {START} to {END})")
print(f"{'Pair':<15} {'Sector':<15} {'p-value':>8}")
for v in final:
    pair_str = f"{v['ticker_a']}/{v['ticker_b']}"
    print(f"{pair_str:<15} {v['sector']:<15} {v['p_value']:>8.4f}")

print(f"\nTotal final pairs: {len(final)}")
print(f"  From existing list: {len(kept)}")
print(f"  New from screener:  {len(screener_validated)}")