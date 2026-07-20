# find_pairs.py  —  full sector-wide pair screener
#
# WHAT THIS DOES
# ==============
# For every within-sector pair in SECTOR_BASKETS, this script measures:
#   1. Return correlation       — do they move together?
#   2. Engle-Granger cointegration at 5 lookbacks (1y / 2y / 3y / 4y / 5y)
#   3. OLS hedge ratio (β)      — shares of B per share of A to stay hedged
#   4. Half-life of mean reversion — how fast the spread heals a gap
#
# Results are sorted by (windows_passed DESC, half_life ASC, best_p ASC) and
# written to pairs_screen_results.csv.  Three buckets are printed to stdout:
#   GREEN            — passes ≥3 windows AND half-life ≤20d  (trade-ready)
#   STURDY BUT SLOW  — passes ≥3 windows but half-life >20d
#   FAST BUT FRAGILE — fast half-life but only 1-2 windows
#
# After running, validate your top candidates through the API:
#   curl "http://localhost:5050/api/cointegration?ticker_a=TMO&ticker_b=IQV&start=2020-01-01"
# Keep only pairs where "is_cointegrated": true.
#
# HOW TO RUN
# ==========
#   cd correlation-api
#   pip install yfinance statsmodels pandas numpy
#   python3 scripts/find_pairs.py
#
# ─────────────────────────────────────────────────────────────────────────────
# MATHEMATICAL FOUNDATIONS
# ─────────────────────────────────────────────────────────────────────────────
#
# 1. COINTEGRATION (Engle-Granger, 1987)
# ----------------------------------------
# Two I(1) price series Xₜ and Yₜ (random walks individually) are cointegrated
# if there exists a coefficient β such that the linear combination
#
#       Zₜ = Xₜ − β·Yₜ
#
# is I(0) — i.e. stationary (mean-reverting around a fixed level).  A stationary
# spread means deviations from the long-run equilibrium are temporary, which is
# exactly what a pairs-trading strategy exploits.
#
# The Engle-Granger procedure:
#   Step 1 — regress Xₜ on Yₜ via OLS to estimate β̂ and form residuals Ẑₜ.
#   Step 2 — run an Augmented Dickey-Fuller (ADF) test on Ẑₜ:
#             H₀: Ẑₜ has a unit root  →  spread is NOT mean-reverting
#             H₁: Ẑₜ is stationary   →  spread IS mean-reverting
#   p < 0.05 → reject H₀ → the spread is stationary → tradeable.
#
# We test at 5 windows (1 / 2 / 3 / 4 / 5 years of daily bars).  "windows_passed"
# counts how many of the 5 return p < 0.05.  More windows = more time-stable
# relationship.  Passes 1 window → could be a data artefact.  Passes 4-5 → robust.
#
# 2. HEDGE RATIO (β via OLS)
# ---------------------------
# OLS regression:  Xₜ = α + β·Yₜ + εₜ
#
# β tells you how many shares of Y to short per share of X so that the combined
# position (long X, short β·Y) creates a dollar-neutral spread Zₜ = Xₜ − β·Yₜ.
# This spread is what we then test for stationarity.
#
# 3. RETURN CORRELATION
# ----------------------
# Pearson r of daily returns:  rₜ = (Pₜ − Pₜ₋₁) / Pₜ₋₁
#
# Returns (not prices) are used to avoid spurious correlation: two trending stocks
# show high price-level correlation even with no causal relationship.  Return
# correlation is a genuine co-movement signal.
#
# Note: correlation ≠ cointegration.  High correlation means they move in the same
# direction daily.  Cointegration means their SPREAD is bounded — a much stronger
# and more directly useful property for trading.
#
# 4. HALF-LIFE OF MEAN REVERSION (Ornstein-Uhlenbeck / AR(1))
# -------------------------------------------------------------
# Assume the spread Zₜ follows a discrete OU process:
#
#       ΔZₜ = α + λ·Zₜ₋₁ + εₜ          AR(1) on spread changes
#
# λ̂ is estimated by OLS.  For a mean-reverting spread: λ < 0 (a large spread
# yesterday tends to shrink today).  Half-life in trading days:
#
#       HL = −ln(2) / λ
#
# Interpretation:
#   HL < 5d    → very short; execution + slippage risk dominates
#   5–30d      → short-term mean reversion; realistic to trade
#   30–100d    → medium-term; hold weeks; valid for swing-style strategies
#   > 100d     → more of a long-horizon relative-value bet
#   λ ≥ 0      → spread is trending (not mean-reverting) → HL = NaN
#
# ─────────────────────────────────────────────────────────────────────────────
# WHY WITHIN-SECTOR (AND ESPECIALLY DUOPOLIES)
# ─────────────────────────────────────────────────────────────────────────────
# Cointegration across unrelated businesses (e.g. a bank vs a chip maker) is
# almost always a statistical coincidence with no economic anchor.  If the shared
# driver disappears, the spread blows up and the position has no reason to revert.
#
# Same-sector pairs share demand drivers, cost structures, and often the same
# customer base, so a stable price ratio is economically defensible.  This is
# especially true for near-duopolies (e.g. WM/RSG in waste, AZO/ORLY in auto
# parts, MLM/VMC in aggregates): the two companies sell literally the same
# product and price-match each other, creating structural gravity on the ratio.

import itertools
import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm


# ---- config -----------------------------------------------------------------

INTERVAL = "1d"
BARS_PER_YEAR = 252
WINDOWS_YEARS = [1, 2, 3, 4, 5]
PVALUE_CUTOFF = 0.05
HALFLIFE_YEARS = 2        # half-life measured on the most recent 2 years
MAX_YEARS = max(WINDOWS_YEARS)
CSV_OUT = "pairs_screen_results.csv"


# ---- sector baskets ---------------------------------------------------------
# Two rounds of baskets merged into one.  Round 1 covered broad sector peers;
# Round 2 drilled into tighter sub-industries and near-duopolies.

SECTOR_BASKETS = {
    # ── Round 1: broad sector peers ──────────────────────────────────────────
    "US banks":                ["JPM", "BAC", "C", "WFC", "USB", "PNC", "TFC", "KEY", "RF", "FITB"],
    "i-banks & brokers":       ["GS", "MS", "SCHW", "RJF", "AMP", "BK"],
    "payments & cards":        ["V", "MA", "AXP", "COF", "PYPL", "GPN"],
    "asset managers":          ["BX", "KKR", "APO", "BLK", "ARES", "TROW", "CG"],
    "semiconductors":          ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "TXN", "ADI", "MU", "AMAT", "LRCX"],
    "mega-tech & software":    ["MSFT", "AAPL", "GOOGL", "META", "AMZN", "ORCL", "CRM", "ADBE"],
    "retail":                  ["WMT", "TGT", "COST", "HD", "LOW", "TJX", "ROST", "DG", "DLTR"],
    "consumer staples":        ["PG", "CL", "KMB", "KO", "PEP", "MDLZ", "KHC", "GIS", "HSY"],
    "restaurants":             ["MCD", "YUM", "SBUX", "CMG", "QSR", "DRI"],
    "oil & gas":               ["XOM", "CVX", "COP", "EOG", "OXY", "DVN", "MPC", "VLO", "PSX"],
    "airlines":                ["DAL", "UAL", "AAL", "LUV", "ALK"],
    "telecom":                 ["VZ", "T", "TMUS"],
    "pharma":                  ["PFE", "MRK", "JNJ", "ABBV", "BMY", "LLY", "AMGN", "GILD", "BIIB"],
    "health insurers":         ["UNH", "ELV", "CI", "CVS", "HUM", "CNC"],
    "med devices":             ["MDT", "SYK", "ABT", "ISRG", "BSX", "BDX"],
    "industrials/machinery":   ["CAT", "DE", "HON", "GE", "EMR", "ETN", "ITW", "PH"],
    "defense/aerospace":       ["LMT", "NOC", "GD", "RTX", "BA", "LHX"],
    "rails & freight":         ["UNP", "CSX", "NSC", "UPS", "FDX"],
    "insurance":               ["MET", "PRU", "AIG", "CB", "TRV", "ALL", "PGR"],
    "media":                   ["NFLX", "DIS", "CMCSA", "FOXA", "WBD"],
    "homebuilders":            ["DHI", "LEN", "PHM", "NVR", "TOL"],
    "chemicals":               ["DOW", "LYB", "DD", "APD", "LIN", "ECL"],
    "utilities":               ["DUK", "SO", "D", "AEP", "EXC", "NEE", "XEL", "WEC"],
    "REITs (diversified)":     ["AMT", "CCI", "PLD", "O", "SPG", "PSA", "EXR"],
    "materials/metals":        ["FCX", "SCCO", "NUE", "STLD", "NEM"],

    # ── Round 2: tight sub-industries & near-duopolies ───────────────────────
    "credit ratings & data":   ["SPGI", "MCO", "MSCI", "FDS", "MORN", "VRSK"],
    "exchanges":               ["CME", "ICE", "NDAQ", "CBOE", "MKTX", "TW"],
    "payroll / HCM":           ["ADP", "PAYX", "PCTY", "PAYC", "NSP"],
    "regional banks":          ["ZION", "HBAN", "MTB", "CFG", "COLB", "CMA", "WAL", "EWBC", "SNV"],
    "insurance brokers":       ["AJG", "BRO", "MMC", "AON", "WTW"],
    "consumer finance":        ["SYF", "ALLY", "SLM", "NAVI", "OMF"],
    "payment processors":      ["FIS", "FI", "JKHY"],
    "aggregates / cement":     ["MLM", "VMC", "EXP", "USLM"],
    "paint / coatings":        ["SHW", "PPG", "RPM", "AXTA"],
    "specialty chemicals":     ["CE", "EMN", "ALB", "FMC", "IFF", "HUN"],
    "fertilizers / ag":        ["NTR", "MOS", "CF", "CTVA"],
    "steel":                   ["RS", "CLF", "CMC", "ATI"],
    "precious metals miners":  ["GOLD", "AEM", "KGC", "FNV", "WPM"],
    "truck / ag machinery":    ["PCAR", "CMI", "OSK", "TEX", "AGCO"],
    "electrical equipment":    ["NVT", "HUBB", "GNRC", "AYI"],
    "waste / environmental":   ["WM", "RSG", "CWST", "GFL", "CLH"],
    "HVAC / building":         ["TT", "LII", "WSO", "AOS", "JCI", "CARR"],
    "aerospace suppliers":     ["HWM", "TDG", "HEI", "CW"],
    "logistics / freight":     ["CHRW", "EXPD", "JBHT", "XPO", "KNX"],
    "auto parts retail":       ["AZO", "ORLY", "GPC", "AAP"],
    "grocery":                 ["KR", "ACI", "SFM"],
    "apparel / footwear":      ["NKE", "LULU", "DECK", "RL", "TPR", "CPRI"],
    "packaged food":           ["CAG", "CPB", "SJM", "HRL", "TSN", "MKC"],
    "beverages":               ["STZ", "TAP", "SAM", "KDP", "MNST"],
    "household / personal":    ["EL", "CLX", "CHD", "KVUE"],
    "tobacco":                 ["MO", "PM", "BTI"],
    "restaurants (QSR)":       ["DPZ", "WING", "TXRH", "EAT", "CAVA"],
    "EV makers":               ["TSLA", "RIVN", "LCID"],
    "legacy autos":            ["F", "GM", "STLA"],
    "cruise lines":            ["CCL", "RCL", "NCLH"],
    "hotels":                  ["MAR", "HLT", "H", "WH"],
    "online travel":           ["BKNG", "EXPE", "ABNB", "TRIP"],
    "casinos":                 ["LVS", "WYNN", "MGM", "CZR", "BYD"],
    "biotech":                 ["REGN", "VRTX", "ALNY", "INCY", "EXEL", "NBIX"],
    "life science tools":      ["TMO", "DHR", "A", "MTD", "WAT", "IQV"],
    "drug distributors":       ["MCK", "COR", "CAH"],
    "hospitals":               ["HCA", "THC", "UHS"],
    "cybersecurity":           ["CRWD", "PANW", "FTNT", "ZS", "OKTA"],
    "enterprise SaaS":         ["NOW", "WDAY", "SNOW", "TEAM", "DDOG", "NET", "MDB"],
    "hardware / storage":      ["DELL", "HPQ", "HPE", "NTAP", "STX", "WDC"],
    "networking":              ["CSCO", "ANET", "FFIV", "CIEN"],
    "midstream / pipelines":   ["KMI", "WMB", "OKE", "ET", "EPD", "TRGP"],
    "oil services":            ["BKR", "NOV", "FTI"],
    "E&P":                     ["FANG", "CTRA", "APA", "EQT", "AR", "RRC"],
    "solar / clean":           ["FSLR", "ENPH", "SEDG", "RUN"],
    "utilities (mid-cap)":     ["PCG", "ED", "EIX", "PEG", "SRE", "PPL", "FE", "AEE"],
    "apartment REITs":         ["AVB", "EQR", "ESS", "MAA", "UDR", "CPT"],
    "healthcare REITs":        ["WELL", "VTR", "HR", "OHI", "DOC", "SBRA"],
    "industrial REITs":        ["FR", "EGP", "STAG", "REXR"],
    "retail REITs":            ["KIM", "REG", "FRT", "BRX"],
    "data center / tower":     ["EQIX", "DLR", "SBAC"],
    "net lease REITs":         ["WPC", "NNN", "ADC"],
}


# ── data layer ───────────────────────────────────────────────────────────────

def pull_all_closes(pairs):
    tickers = sorted({t for _, a, b in pairs for t in (a, b)})
    raw = yf.download(tickers, period=f"{MAX_YEARS}y", interval=INTERVAL,
                      auto_adjust=True, progress=False)
    return raw["Close"], tickers


# ── measurements ─────────────────────────────────────────────────────────────

def cointegration_pvalue(a, b):
    # Engle-Granger ADF on OLS residuals.  p < 0.05 → spread is stationary.
    _, pvalue, _ = coint(a, b)
    return pvalue


def hedge_ratio_beta(a, b):
    # OLS: Xₜ = α + β·Yₜ + εₜ  →  β shares of Y per share of X for neutral spread
    model = sm.OLS(a, sm.add_constant(b)).fit()
    return model.params[1]


def return_correlation(a, b):
    # Pearson r of daily returns (not prices) to avoid spurious trend correlation.
    ra = np.diff(a) / a[:-1]
    rb = np.diff(b) / b[:-1]
    return np.corrcoef(ra, rb)[0, 1]


def half_life_of_reversion(spread):
    # AR(1): ΔZₜ = α + λ·Zₜ₋₁ + εₜ  →  HL = −ln(2)/λ  [trading days]
    # λ ≥ 0 means trending (not mean-reverting) → return NaN.
    spread = np.asarray(spread, dtype=float)
    level = spread[:-1]
    change = np.diff(spread)
    model = sm.OLS(change, sm.add_constant(level)).fit()
    lam = model.params[1]
    if lam >= 0:
        return np.nan
    return -np.log(2) / lam


def tail(arr, n):
    return arr[-n:] if len(arr) > n else arr


# ── main screen ──────────────────────────────────────────────────────────────

def build_pair_list():
    seen = set()
    pairs = []
    for sector, tickers in SECTOR_BASKETS.items():
        for a, b in itertools.combinations(tickers, 2):
            key = frozenset((a, b))
            if key in seen:
                continue
            seen.add(key)
            pairs.append((sector, a, b))
    return pairs


def run_screen():
    pairs = build_pair_list()
    print(f"universe: {len(pairs)} within-sector pairs across {len(SECTOR_BASKETS)} baskets")
    print("downloading price data...")
    closes, tickers = pull_all_closes(pairs)
    print(f"got {len([t for t in tickers if t in closes.columns])}/{len(tickers)} tickers\n")

    rows = []
    for sector, ta, tb in pairs:
        label = f"{ta}/{tb}"
        if ta not in closes.columns or tb not in closes.columns:
            continue

        pair = closes[[ta, tb]].dropna()
        if len(pair) < BARS_PER_YEAR:
            continue

        a_full = pair[ta].to_numpy()
        b_full = pair[tb].to_numpy()

        row = {"sector": sector, "pair": label, "bars": len(pair)}
        try:
            passed, pvals = 0, []
            for years in WINDOWS_YEARS:
                n = years * BARS_PER_YEAR
                pv = cointegration_pvalue(tail(a_full, n), tail(b_full, n))
                row[f"p_{years}y"] = pv
                pvals.append(pv)
                if pv < PVALUE_CUTOFF:
                    passed += 1
            row["windows_passed"] = passed
            row["best_p"] = min(pvals)
            row["corr"] = return_correlation(a_full, b_full)
            row["beta"] = hedge_ratio_beta(a_full, b_full)
            recent = tail(pair[ta].to_numpy() / pair[tb].to_numpy(),
                          HALFLIFE_YEARS * BARS_PER_YEAR)
            row["half_life_days"] = half_life_of_reversion(recent)
        except Exception as e:
            print(f"  {label}: error — {e}")
            continue

        rows.append(row)

    table = pd.DataFrame(rows)
    if table.empty:
        print("no usable data.")
        return table

    hl = table["half_life_days"]
    table["_hl_rank"] = np.where((hl > 0) & (hl < 500), hl, 9999)
    table = table.sort_values(["windows_passed", "_hl_rank", "best_p"],
                              ascending=[False, True, True]).reset_index(drop=True)

    pcols = [f"p_{y}y" for y in WINDOWS_YEARS]
    out = table[["sector", "pair", "corr"] + pcols +
                ["windows_passed", "beta", "half_life_days", "bars"]].copy()
    out.to_csv(CSV_OUT, index=False)
    print(f"full results ({len(out)} pairs) → {CSV_OUT}\n")

    fast   = (table["half_life_days"] > 0) & (table["half_life_days"] <= 20)
    sturdy = table["windows_passed"] >= 3

    green        = table[sturdy & fast]
    sturdy_slow  = table[sturdy & ~fast]
    fast_fragile = table[~sturdy & (table["windows_passed"] >= 1) & fast]

    def show(df):
        for _, r in df.iterrows():
            hl = r["half_life_days"]
            hl_s = f"{hl:5.1f}d" if np.isfinite(hl) else "  n/a"
            grid = "".join("Y" if r[f"p_{y}y"] < PVALUE_CUTOFF else "." for y in WINDOWS_YEARS)
            print(f"  {r['pair']:<11} {r['sector']:<26} "
                  f"1-5y[{grid}] p*={r['best_p']:.4f} corr={r['corr']:.2f} "
                  f"beta={r['beta']:5.2f} half-life={hl_s}")

    print("=" * 92)
    print(f"GREEN — sturdy (≥3 windows) AND fast (half-life ≤20d)  [{len(green)}]")
    print("  sweet spot: real relationship + heals fast enough to actually trade")
    print("=" * 92)
    show(green) if not green.empty else print("  none")

    print("\n" + "=" * 92)
    print(f"STURDY BUT SLOW — ≥3 windows, half-life >20d  [{len(sturdy_slow)}]")
    print("  real relationship but you'd hold weeks-to-months")
    print("=" * 92)
    show(sturdy_slow) if not sturdy_slow.empty else print("  none")

    print("\n" + "=" * 92)
    print(f"FAST BUT FRAGILE — fast half-life but only 1-2 windows  [{len(fast_fragile)}]")
    print("  snappy but not stable across time — treat as suspect")
    print("=" * 92)
    show(fast_fragile) if not fast_fragile.empty else print("  none")

    print("\n" + "-" * 60)
    print(f"pairs passing per window (out of {len(table)}):")
    for y in WINDOWS_YEARS:
        print(f"  {y}y: {(table[f'p_{y}y'] < PVALUE_CUTOFF).sum()}")

    return table


if __name__ == "__main__":
    run_screen()
