# Correlation Trading API

Flask backend powering the **Correlation Trading** page on the clubsite. Computes lagged correlation and spread metrics for stock pairs on demand, using Yahoo Finance data fetched via `yfinance`.

## Run

```bash
cd correlation-api
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Defaults to **port 5050**. Override with `CORRELATION_API_PORT=5060 python app.py`.

The Next dev server (`npm run dev` in the repo root) rewrites browser requests from `/api/*` to `http://localhost:5050/api/*`, so the site Just Works once both are running.

## Endpoints

| Method | Path | Query | Returns |
|--------|------|-------|---------|
| GET | `/api/pairs` | — | All 28 pre-configured pairs (tickers, names, sector, category) |
| GET | `/api/validate` | `ticker` | `{valid, ticker, name}` — used to validate custom ticker input |
| GET | `/api/correlation` | `ticker_a`, `ticker_b`, `start`, `end`, `max_lag` | Lagged Pearson correlation across `[-max_lag, +max_lag]` |
| GET | `/api/spread` | `ticker_a`, `ticker_b`, `start`, `end`, `spread_type` | Spread series, z-score, and metrics for the pair |
| GET | `/api/risk/breakdown` | `ticker_a`, `ticker_b`, optional `end`, optional `start` override | Correlation-breakdown risk signal with its own lookback window, current 60d correlation, 1y baseline, and `broken_since` |
| GET | `/api/cointegration` | `ticker_a`, `ticker_b`, `start` (default `2020-01-01`), `end` (default today) | Engle-Granger cointegration test: `{test_stat, p_value, is_cointegrated}` |

Dates are `YYYY-MM-DD`. `spread_type` is one of the values supported by `analysis/spread.py` (default `log_ratio`).

## How data is pulled

1. **Browser request** lands on the Flask endpoint (e.g. `/api/correlation?ticker_a=MSFT&ticker_b=GOOGL&start=2023-01-01&end=2026-01-01`).
2. **`load_pair_data`** (`analysis/data_loader.py`) fetches each ticker via `get_stock_data`, then inner-joins on `Date`.
3. **`get_stock_data`** is the cache layer:
   - Looks for `data/raw/<TICKER>_<start>_to_<end>_raw.csv` — if present, reads it and returns immediately.
   - Otherwise calls `yfinance.download(ticker, start, end)`, normalises columns to `[Date, Close, Ticker]`, writes the CSV, and returns.
4. **Analysis modules** (`correlation.py`, `spread.py`) consume the merged DataFrame and produce the JSON the frontend renders.

The cache key is the **exact** `(ticker, start, end)` tuple, so different date ranges produce different files. Cache files live under `correlation-api/data/raw/` and are gitignored — wipe them anytime to force a fresh fetch.

```
correlation-api/
├── app.py                    # Flask app + route handlers
├── analysis/
│   ├── data_loader.py        # yfinance fetch + CSV cache
│   ├── correlation.py        # Lagged Pearson
│   └── spread.py             # Hedge ratio, spread series, z-score, metrics
├── data/raw/                 # CSV cache (gitignored)
└── requirements.txt
```

## Configuring the pair list

Edit `PAIRS` at the top of `app.py`. Each entry needs `ticker_a`, `ticker_b`, `name_a`, `name_b`, `sector`. The frontend picks these up via `GET /api/pairs`.

## Pair curation methodology

Every pair in the **Most Tradeable** tab must pass an Engle-Granger cointegration test (p < 0.05) on the **2020-01-01 to June 2026** window before being added. The current 14 validated pairs were selected using this process and should be re-run each term:

**Step 1 — Candidate generation**

Run a sector screener across a broad universe of tickers (300+ pairs across 25+ sectors), testing cointegration at multiple time windows (1y / 2y / 3y / 4y / 5y). Pairs that pass more windows are more robust candidates. Record the half-life of mean reversion (shorter = faster spread convergence = more tradeable).

**Step 2 — Validation through the API**

For the top candidates (those passing 3+ windows and half-life < 100 days), run each through our endpoint:

```bash
curl "http://localhost:5050/api/cointegration?ticker_a=TMO&ticker_b=IQV&start=2020-01-01"
```

Keep only pairs where `"is_cointegrated": true` (p < 0.05).

**Step 3 — Update `PAIRS`**

Replace the list in `app.py`. Include only validated pairs. Sort by sector for readability.

**Current validated pairs (as of July 2026):**

| Pair | Sector | p-value | Half-life |
|------|--------|---------|-----------|
| STX/WDC | Technology | 0.0003 | 71d |
| ADI/AMAT | Technology | 0.0019 | — |
| LLY/AMGN | Healthcare | 0.0021 | — |
| PNC/FITB | Financials | 0.0027 | — |
| GS/BK | Financials | 0.0034 | — |
| WMB/EPD | Energy | 0.0037 | 31d |
| TMO/MTD | Healthcare | 0.0088 | 25d |
| TMO/IQV | Healthcare | 0.0091 | 17d |
| REG/BRX | Real Estate | 0.0146 | 23d |
| UDR/CPT | Real Estate | 0.0188 | 26d |
| A/IQV | Healthcare | 0.0221 | 29d |
| MS/BK | Financials | 0.0257 | — |
| UNP/CSX | Industrials | 0.0404 | — |
| ABNB/TRIP | Consumer | 0.0468 | 57d |

## Troubleshooting

- **`Connection refused` from the site** → Flask isn't running, or it's on a port other than 5050. Check the rewrite in `../next.config.mjs`.
- **`yfinance` returns empty** → ticker symbol invalid, or Yahoo throttled the IP. Delete the cached CSV (if any) and retry; switch networks if it persists.
- **Stale data** → cache is keyed by date range. Delete files in `data/raw/` to refetch.
