import os
import math
from datetime import date
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

from analysis.data_loader import load_pair_data
from analysis.correlation import compute_lagged_correlation
from analysis.spread import calculate_spread_metrics

app = Flask(__name__)
CORS(app)

PAIRS = [
    {"ticker_a": "MSFT",  "ticker_b": "GOOGL", "name_a": "Microsoft",         "name_b": "Google",            "sector": "Technology"},
    {"ticker_a": "AMD",   "ticker_b": "NVDA",  "name_a": "AMD",               "name_b": "NVIDIA",            "sector": "Technology"},
    {"ticker_a": "CVS",   "ticker_b": "JNJ",   "name_a": "CVS Health",        "name_b": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker_a": "PFE",   "ticker_b": "MRK",   "name_a": "Pfizer",            "name_b": "Merck",             "sector": "Healthcare"},
    {"ticker_a": "CL",    "ticker_b": "KMB",   "name_a": "Colgate-Palmolive", "name_b": "Kimberly-Clark",    "sector": "Consumer"},
    {"ticker_a": "KO",    "ticker_b": "PEP",   "name_a": "Coca-Cola",         "name_b": "PepsiCo",           "sector": "Consumer"},
    {"ticker_a": "COST",  "ticker_b": "BJ",    "name_a": "Costco",            "name_b": "BJ's Wholesale",    "sector": "Consumer"},
    {"ticker_a": "GE",    "ticker_b": "BA",    "name_a": "GE Aerospace",      "name_b": "Boeing",            "sector": "Industrials"},
    {"ticker_a": "V",     "ticker_b": "MA",    "name_a": "Visa",              "name_b": "Mastercard",        "sector": "Financials"},
    {"ticker_a": "MS",    "ticker_b": "GS",    "name_a": "Morgan Stanley",    "name_b": "Goldman Sachs",     "sector": "Financials"},
    {"ticker_a": "JPM",   "ticker_b": "BAC",   "name_a": "JPMorgan Chase",    "name_b": "Bank of America",   "sector": "Financials"},
    {"ticker_a": "XOM",   "ticker_b": "CVX",   "name_a": "ExxonMobil",        "name_b": "Chevron",           "sector": "Energy"},
    {"ticker_a": "T",     "ticker_b": "VZ",    "name_a": "AT&T",              "name_b": "Verizon",           "sector": "Telecom"},
    {"ticker_a": "WMT",   "ticker_b": "TGT",   "name_a": "Walmart",           "name_b": "Target",            "sector": "Retail"},
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


if __name__ == "__main__":
    port = int(os.environ.get("CORRELATION_API_PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
