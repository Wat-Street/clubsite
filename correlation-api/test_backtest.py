import os
import unittest
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from analysis.backtest import generate_zscore_signals, run_backtest

class TestBacktestHarness(unittest.TestCase):
    def setUp(self):
        # Create a simple 10-day synthetic price series
        # Day:         0     1     2     3     4     5     6     7     8     9
        # Price A:   100   102   104   102   100    98    96    98   100   102
        # Price B:   100   100   100   100   100   100   100   100   100   100
        # Spread:      0     2     4     2     0    -2    -4    -2     0     2
        dates = pd.date_range(start="2026-05-01", periods=10)
        self.prices_a = pd.Series([100.0, 102.0, 104.0, 102.0, 100.0, 98.0, 96.0, 98.0, 100.0, 102.0], index=dates)
        self.prices_b = pd.Series([100.0] * 10, index=dates)
        self.spread = self.prices_a - self.prices_b
        
        # Test signal sequence:
        # Day 0: 0
        # Day 1: 0
        # Day 2: -1 (Short spread - Short A, Long B)
        # Day 3: -1
        # Day 4: 0  (Closed trade - Flat)
        # Day 5: 1  (Long spread - Long A, Short B)
        # Day 6: 1
        # Day 7: 0  (Closed trade - Flat)
        # Day 8: 0
        # Day 9: 0
        self.signals = pd.Series([0, 0, -1, -1, 0, 1, 1, 0, 0, 0], index=dates)

    def test_run_backtest_metrics(self):
        # Run the backtester
        results = run_backtest(self.prices_a, self.prices_b, self.signals, hedge_ratio=1.0)
        
        self.assertIn("equity_curve", results)
        self.assertIn("sharpe", results)
        self.assertIn("max_dd", results)
        self.assertIn("num_trades", results)
        self.assertIn("win_rate", results)
        self.assertIn("trade_log", results)
        
        # We had 2 trades completed:
        # Trade 1: Short spread entered at index 2 (price_a=104, price_b=100, spread=4)
        #          Closed at index 4 (price_a=100, price_b=100, spread=0)
        #          For short: spread_entry (4) - spread_exit (0) = +4 P&L. Profit!
        # Trade 2: Long spread entered at index 5 (price_a=98, price_b=100, spread=-2)
        #          Closed at index 7 (price_a=98, price_b=100, spread=-2)
        #          For long: spread_exit (-2) - spread_entry (-2) = 0 P&L. Flat!
        self.assertEqual(results["num_trades"], 2)
        
        trade1 = results["trade_log"][0]
        self.assertEqual(trade1["type"], "SHORT")
        self.assertEqual(trade1["pnl_val"], 4.0)
        
        trade2 = results["trade_log"][1]
        self.assertEqual(trade2["type"], "LONG")
        self.assertEqual(trade2["pnl_val"], 0.0)

    def test_generate_zscore_signals(self):
        # Verify signal generator doesn't crash and returns signals and zscore
        signals, zscore = generate_zscore_signals(self.spread, window=5, entry_z=1.0, exit_z=0.0)
        self.assertEqual(len(signals), len(self.spread))
        self.assertEqual(len(zscore), len(self.spread))

    def test_api_integration(self):
        from unittest.mock import patch
        from app import app
        import pandas as pd
        import numpy as np
        
        # Create synthetic DataFrame matching load_pair_data output schema
        dates = pd.date_range(start="2023-01-01", periods=100)
        # MSFT oscillates, GOOGL is flat at 100.0 to generate spread fluctuations
        prices_msft = 100.0 + 5.0 * np.sin(np.arange(100) / 3.0)
        prices_googl = [100.0] * 100
        mock_df = pd.DataFrame({
            "Date": dates,
            "Close_MSFT": prices_msft,
            "Ticker_MSFT": ["MSFT"] * 100,
            "Close_GOOGL": prices_googl,
            "Ticker_GOOGL": ["GOOGL"] * 100
        })
        
        with patch("app.load_pair_data") as mock_load:
            mock_load.return_value = mock_df
            with app.test_client() as client:
                resp = client.get("/api/backtest?ticker_a=MSFT&ticker_b=GOOGL&window=20&entry_z=1.0&exit_z=0.0")
                self.assertEqual(resp.status_code, 200)
                data = resp.get_json()
                
                # Check fields
                self.assertEqual(data["ticker_a"], "MSFT")
                self.assertEqual(data["ticker_b"], "GOOGL")
                self.assertIn("metrics", data)
                self.assertIn("equity_curve", data)
                self.assertIn("trade_log", data)
                
                metrics = data["metrics"]
                self.assertIn("sharpe", metrics)
                self.assertIn("max_drawdown", metrics)
                self.assertIn("num_trades", metrics)
                self.assertIn("win_rate", metrics)
                
                print(f"\n[API MOCK TEST SUCCESS] Sharpe: {metrics['sharpe']:.4f}, Max DD: {metrics['max_drawdown']:.4f}, Trades: {metrics['num_trades']}, Win Rate: {metrics['win_rate']:.4%}")

    def test_spread_api_uses_window_for_zscore_not_hedge_ratio(self):
        from unittest.mock import patch
        from app import app
        import numpy as np

        dates = pd.date_range(start="2023-01-01", periods=100)
        mock_df = pd.DataFrame({
            "Date": dates,
            "Close_MSFT": 100.0 + np.arange(100) * 0.5,
            "Ticker_MSFT": ["MSFT"] * 100,
            "Close_GOOGL": [100.0] * 100,
            "Ticker_GOOGL": ["GOOGL"] * 100,
        })

        with patch("app.load_pair_data") as mock_load:
            mock_load.return_value = mock_df
            with app.test_client() as client:
                resp = client.get(
                    "/api/spread?ticker_a=MSFT&ticker_b=GOOGL&window=20&spread_type=log_ratio"
                )
                self.assertEqual(resp.status_code, 200)
                data = resp.get_json()
                metrics = data["metrics"]

                self.assertLess(abs(metrics["current"]), 1.0)
                self.assertEqual(metrics["zscore_window"], 20.0)
                self.assertIn("current_mean", metrics)
                self.assertIn("current_std", metrics)

                expected_zscore = (
                    metrics["current"] - metrics["current_mean"]
                ) / metrics["current_std"]
                self.assertAlmostEqual(
                    metrics["current_zscore"],
                    expected_zscore,
                    places=6,
                )

    def test_stock_data_cache_path_is_versioned(self):
        from analysis.data_loader import CACHE_VERSION, get_data_path

        path = get_data_path("MSFT", "2023-01-01", "2023-02-01")
        self.assertIn(f"_{CACHE_VERSION}_raw.csv", path)

    def test_stock_downloads_are_serialized(self):
        from unittest.mock import patch
        from analysis.data_loader import get_stock_data

        active = 0
        max_active = 0
        active_lock = threading.Lock()

        def fake_download(ticker, *args, **kwargs):
            nonlocal active, max_active
            with active_lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.02)
            with active_lock:
                active -= 1

            dates = pd.date_range(start="2023-01-02", periods=3)
            return pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=dates)

        with patch("analysis.data_loader.yf.download", side_effect=fake_download):
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(
                    lambda ticker: get_stock_data(
                        ticker,
                        "2023-01-01",
                        "2023-01-06",
                        cache=False,
                    ),
                    ["AAA", "BBB", "CCC", "DDD"],
                ))

        self.assertEqual(max_active, 1)
        self.assertEqual([df["Ticker"].iloc[0] for df in results], ["AAA", "BBB", "CCC", "DDD"])

if __name__ == "__main__":
    unittest.main()
