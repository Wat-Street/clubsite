import numpy as np
import pandas as pd
import pytest

from analysis.spread import calculate_spread_metrics


class TestSpreadMetricsDifference:
    def test_values(self, simple_pair_df):
        """AAPL=[100,110,105,115,120], MSFT=[50,55,52,58,60] -> diff=[50,55,53,57,60]."""
        result_df, metrics = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="difference"
        )
        expected_spread = [50.0, 55.0, 53.0, 57.0, 60.0]
        for actual, exp in zip(result_df["spread"].tolist(), expected_spread):
            assert actual == pytest.approx(exp, abs=1e-6)

        assert metrics["mean"] == pytest.approx(np.mean(expected_spread), abs=1e-4)
        assert metrics["std"] == pytest.approx(
            pd.Series(expected_spread).std(), abs=1e-4
        )
        assert metrics["min"] == pytest.approx(50.0, abs=1e-4)
        assert metrics["max"] == pytest.approx(60.0, abs=1e-4)
        assert metrics["current"] == pytest.approx(60.0, abs=1e-4)

        # current_zscore = (60 - mean) / std
        mean = np.mean(expected_spread)
        std = pd.Series(expected_spread).std()
        assert metrics["current_zscore"] == pytest.approx((60.0 - mean) / std, abs=1e-4)


class TestSpreadMetricsRatio:
    def test_values(self, simple_pair_df):
        result_df, metrics = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="ratio"
        )
        expected_spread = [100/50, 110/55, 105/52, 115/58, 120/60]
        for actual, exp in zip(result_df["spread"].tolist(), expected_spread):
            assert actual == pytest.approx(exp, abs=1e-6)

        assert metrics["current"] == pytest.approx(120.0 / 60.0, abs=1e-4)


class TestSpreadMetricsLogRatio:
    def test_values(self, simple_pair_df):
        result_df, metrics = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="log_ratio"
        )
        expected_spread = [np.log(100/50), np.log(110/55), np.log(105/52),
                           np.log(115/58), np.log(120/60)]
        for actual, exp in zip(result_df["spread"].tolist(), expected_spread):
            assert actual == pytest.approx(exp, abs=1e-6)


class TestSpreadMetricsStructure:
    def test_result_df_columns(self, simple_pair_df):
        result_df, _ = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="difference"
        )
        assert list(result_df.columns) == [
            "Date", "AAPL_price", "MSFT_price", "spread", "zscore"
        ]

    def test_result_df_length(self, simple_pair_df):
        result_df, _ = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="difference"
        )
        assert len(result_df) == len(simple_pair_df)

    def test_num_observations(self, simple_pair_df):
        _, metrics = calculate_spread_metrics(
            simple_pair_df, "AAPL", "MSFT", spread_type="difference"
        )
        assert metrics["num_observations"] == 5

    def test_invalid_spread_type(self, simple_pair_df):
        with pytest.raises(ValueError, match="Unknown spread_type"):
            calculate_spread_metrics(
                simple_pair_df, "AAPL", "MSFT", spread_type="invalid"
            )

    def test_zero_price_in_log_ratio(self):
        """Zero price should produce NaN spread, not crash."""
        df = pd.DataFrame({
            "Date": pd.date_range("2024-01-01", periods=3, freq="B"),
            "Close_A": [10.0, 20.0, 30.0],
            "Close_B": [5.0, 0.0, 10.0],
        })
        result_df, metrics = calculate_spread_metrics(df, "A", "B", spread_type="log_ratio")
        assert not np.isnan(result_df["spread"].iloc[0])
        assert np.isnan(result_df["spread"].iloc[1])
        assert not np.isnan(result_df["spread"].iloc[2])
        # num_observations should exclude the NaN row
        assert metrics["num_observations"] == 2
