import os
import math
from datetime import date
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

import yfinance as yf

from analysis.data_loader import load_pair_data
from analysis.correlation import compute_lagged_correlation
from analysis.spread import calculate_spread_metrics
from analysis.screener import screen_sector, SECTOR_TICKERS

app = Flask(__name__)
CORS(app)

PAIRS = [
    # Technology
    # (no pairs passed cointegration in tech sector, 2020-present window)

    # Healthcare
    {"ticker_a": "DHR",  "ticker_b": "IQV",  "name_a": "Danaher",                "name_b": "IQVIA Holdings",          "sector": "Healthcare"},
    {"ticker_a": "TMO",  "ticker_b": "MTD",  "name_a": "Thermo Fisher Scientific","name_b": "Mettler-Toledo",          "sector": "Healthcare"},
    {"ticker_a": "TMO",  "ticker_b": "IQV",  "name_a": "Thermo Fisher Scientific","name_b": "IQVIA Holdings",          "sector": "Healthcare"},
    {"ticker_a": "IQV",  "ticker_b": "MTD",  "name_a": "IQVIA Holdings",          "name_b": "Mettler-Toledo",          "sector": "Healthcare"},

    # Financials
    {"ticker_a": "BLK",  "ticker_b": "COF",  "name_a": "BlackRock",               "name_b": "Capital One",             "sector": "Financials"},
    {"ticker_a": "WFC",  "ticker_b": "AXP",  "name_a": "Wells Fargo",             "name_b": "American Express",        "sector": "Financials"},
    {"ticker_a": "PNC",  "ticker_b": "FITB", "name_a": "PNC Financial",           "name_b": "Fifth Third Bancorp",     "sector": "Financials"},
    {"ticker_a": "GS",   "ticker_b": "BK",   "name_a": "Goldman Sachs",           "name_b": "Bank of New York Mellon", "sector": "Financials"},
    {"ticker_a": "MS",   "ticker_b": "BK",   "name_a": "Morgan Stanley",          "name_b": "Bank of New York Mellon", "sector": "Financials"},
    {"ticker_a": "SCHW", "ticker_b": "MTB",  "name_a": "Charles Schwab",          "name_b": "M&T Bank",                "sector": "Financials"},

    # Energy
    {"ticker_a": "MPC",  "ticker_b": "PSX",  "name_a": "Marathon Petroleum",      "name_b": "Phillips 66",             "sector": "Energy"},
    {"ticker_a": "EPD",  "ticker_b": "BKR",  "name_a": "Enterprise Products",     "name_b": "Baker Hughes",            "sector": "Energy"},
    {"ticker_a": "WMB",  "ticker_b": "KMI",  "name_a": "Williams Companies",      "name_b": "Kinder Morgan",           "sector": "Energy"},
    {"ticker_a": "WMB",  "ticker_b": "EPD",  "name_a": "Williams Companies",      "name_b": "Enterprise Products",     "sector": "Energy"},
    {"ticker_a": "COP",  "ticker_b": "SLB",  "name_a": "ConocoPhillips",          "name_b": "SLB",                     "sector": "Energy"},
    {"ticker_a": "MPC",  "ticker_b": "EPD",  "name_a": "Marathon Petroleum",      "name_b": "Enterprise Products",     "sector": "Energy"},
]

def _safe_float(val):
    try:
        if pd.isna(val):
            return None
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except (TypeError, ValueError):
        return None


@app.route("/api/pairs", methods=["GET"])
def get_pairs():
    return jsonify(PAIRS)


@app.route("/api/validate", methods=["GET"])
def validate_ticker():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"valid": False, "error": "No ticker provided"}), 400
    try:
        info = yf.Ticker(ticker).info
        valid = info.get("regularMarketPrice") is not None or info.get("previousClose") is not None
        name = info.get("shortName", ticker)
        return jsonify({"valid": valid, "ticker": ticker, "name": name if valid else None})
    except Exception:
        return jsonify({"valid": False, "ticker": ticker, "name": None})


@app.route("/api/correlation", methods=["GET"])
def get_correlation():
    ticker_a = request.args.get("ticker_a", "").upper()
    ticker_b = request.args.get("ticker_b", "").upper()
    start = request.args.get("start", "2020-01-01")
    end = request.args.get("end", str(date.today()))
    max_lag = int(request.args.get("max_lag", "10"))

    if not ticker_a or not ticker_b:
        return jsonify({"error": "ticker_a and ticker_b are required"}), 400

    try:
        df = load_pair_data(ticker_a, ticker_b, start, end)
        series_a = df[f"Close_{ticker_a}"]
        series_b = df[f"Close_{ticker_b}"]
        corr_df = compute_lagged_correlation(series_a, series_b, max_lag)

        return jsonify({
            "ticker_a": ticker_a,
            "ticker_b": ticker_b,
            "data": [
                {"lag": int(row["Lag"]), "correlation": _safe_float(row["Correlation"])}
                for _, row in corr_df.iterrows()
            ],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/spread", methods=["GET"])
def get_spread():
    ticker_a = request.args.get("ticker_a", "").upper()
    ticker_b = request.args.get("ticker_b", "").upper()
    start = request.args.get("start", "2023-01-01")
    end = request.args.get("end", str(date.today()))
    spread_type = request.args.get("spread_type", "log_ratio")

    if not ticker_a or not ticker_b:
        return jsonify({"error": "ticker_a and ticker_b are required"}), 400

    try:
        df = load_pair_data(ticker_a, ticker_b, start, end)
        spread_df, metrics = calculate_spread_metrics(df, ticker_a, ticker_b, spread_type)

        price_a = spread_df[f"{ticker_a}_price"]
        price_b = spread_df[f"{ticker_b}_price"]
        norm_a = price_a / price_a.iloc[0] * 100
        norm_b = price_b / price_b.iloc[0] * 100

        data = []
        for i, row in spread_df.iterrows():
            date_val = row["Date"]
            date_str = str(date_val.date()) if hasattr(date_val, "date") and not pd.isna(date_val) else str(date_val)
            data.append({
                "date": date_str,
                "price_a": _safe_float(price_a.iloc[i]),
                "price_b": _safe_float(price_b.iloc[i]),
                "norm_a": _safe_float(norm_a.iloc[i]),
                "norm_b": _safe_float(norm_b.iloc[i]),
                "spread": _safe_float(row["spread"]),
                "zscore": _safe_float(row["zscore"]),
            })

        clean_metrics = {k: _safe_float(v) if isinstance(v, (float, int)) else v for k, v in metrics.items()}

        return jsonify({
            "ticker_a": ticker_a,
            "ticker_b": ticker_b,
            "spread_type": spread_type,
            "data": data,
            "metrics": clean_metrics,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/screener", methods=["GET"])
def get_screener():
    sector = request.args.get("sector", "").lower().strip()
    if not sector:
        return jsonify({"error": "Missing required param: sector"}), 400
    if sector not in SECTOR_TICKERS:
        return jsonify({"error": f"Unknown sector '{sector}'.", "available_sectors": sorted(SECTOR_TICKERS.keys())}), 400
    try:
        min_corr = float(request.args.get("min_corr", 0.70))
    except ValueError:
        return jsonify({"error": "min_corr must be a float between 0 and 1."}), 400
    if not (0.0 <= min_corr <= 1.0):
        return jsonify({"error": "min_corr must be between 0.0 and 1.0."}), 400

    start = request.args.get("start", "2024-01-01")
    end = request.args.get("end", str(date.today()))

    try:
        pairs = screen_sector(SECTOR_TICKERS[sector], start, end, min_corr=min_corr)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"sector": sector, "min_corr": min_corr, "pairs": pairs})

if __name__ == "__main__":
    port = int(os.environ.get("CORRELATION_API_PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
