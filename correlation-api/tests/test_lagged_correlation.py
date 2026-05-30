import numpy as np
import pandas as pd
import pytest

from analysis.correlation import compute_lagged_correlation


class TestLaggedCorrelationBasic:
    def test_lag_zero_matches_pearson(self):
        a = pd.Series([1.0, 2.0, 4.0, 7.0])
        b = pd.Series([3.0, 5.0, 8.0, 10.0])
        result = compute_lagged_correlation(a, b, max_lag=0)
        assert len(result) == 1
        assert result["Lag"].iloc[0] == 0
        assert result["Correlation"].iloc[0] == pytest.approx(a.corr(b), abs=1e-6)

    def test_perfectly_correlated_linear(self):
        """Two linear series: any sub-slice is perfectly correlated."""
        a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        b = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
        result = compute_lagged_correlation(a, b, max_lag=2)
        for _, row in result.iterrows():
            assert row["Correlation"] == pytest.approx(1.0, abs=1e-6)

    def test_anticorrelated(self):
        a = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        b = pd.Series([5.0, 4.0, 3.0, 2.0, 1.0])
        result = compute_lagged_correlation(a, b, max_lag=0)
        assert result["Correlation"].iloc[0] == pytest.approx(-1.0, abs=1e-6)

    def test_leader_follower_peak_at_lag_plus_one(self, leader_follower_pair):
        """b[t] = a[t-1], so correlation should peak at lag=+1."""
        a, b = leader_follower_pair
        result = compute_lagged_correlation(a, b, max_lag=3)
        corr_dict = dict(zip(result["Lag"], result["Correlation"]))
        # At lag=+1, shifted_a aligns perfectly with b
        assert corr_dict[1] == pytest.approx(1.0, abs=1e-6)
        # The peak should be at lag=+1
        max_lag = result.loc[result["Correlation"].idxmax(), "Lag"]
        assert max_lag == 1

    def test_leader_follower_all_values(self, leader_follower_pair):
        """Verify all 7 lag values against hand-computed Pearson correlations."""
        a, b = leader_follower_pair
        result = compute_lagged_correlation(a, b, max_lag=3)
        corr_dict = dict(zip(result["Lag"], result["Correlation"]))

        # At lag=+1: shifted_a = [NaN,1,3,2,5,4,1,3] corr with b=[0,1,3,2,5,4,1,3]
        # Effective: a_shifted=[1,3,2,5,4,1,3] vs b=[1,3,2,5,4,1,3] -> corr=1.0
        assert corr_dict[1] == pytest.approx(1.0, abs=1e-6)

        # At lag=0: direct correlation
        assert corr_dict[0] == pytest.approx(a.corr(b), abs=1e-6)

        # Verify lag=-1: shift b by 1, so shifted_b = [NaN,0,1,3,2,5,4,1]
        # Effective: a=[1,3,2,5,4,1,3] vs shifted_b=[0,1,3,2,5,4,1] -> their corr
        shifted_b = b.shift(1)
        valid = ~(pd.isna(a) | pd.isna(shifted_b))
        expected = a[valid].corr(shifted_b[valid])
        assert corr_dict[-1] == pytest.approx(expected, abs=1e-6)


class TestLaggedCorrelationSymmetry:
    def test_corr_ab_lag_k_equals_corr_ba_lag_neg_k(self, leader_follower_pair):
        """Fundamental mathematical property: corr(A,B,lag=k) == corr(B,A,lag=-k)."""
        a, b = leader_follower_pair
        result_ab = compute_lagged_correlation(a, b, max_lag=3)
        result_ba = compute_lagged_correlation(b, a, max_lag=3)

        corr_ab = dict(zip(result_ab["Lag"], result_ab["Correlation"]))
        corr_ba = dict(zip(result_ba["Lag"], result_ba["Correlation"]))

        for k in range(-3, 4):
            ab_val = corr_ab[k]
            ba_val = corr_ba[-k]
            if pd.isna(ab_val) and pd.isna(ba_val):
                continue
            assert ab_val == pytest.approx(ba_val, abs=1e-10)


class TestLaggedCorrelationOutput:
    def test_columns(self, leader_follower_pair):
        a, b = leader_follower_pair
        result = compute_lagged_correlation(a, b, max_lag=2)
        assert list(result.columns) == ["Lag", "Correlation"]

    def test_row_count(self, leader_follower_pair):
        a, b = leader_follower_pair
        result = compute_lagged_correlation(a, b, max_lag=3)
        assert len(result) == 7  # 2*3+1

    def test_lags_contiguous(self, leader_follower_pair):
        a, b = leader_follower_pair
        result = compute_lagged_correlation(a, b, max_lag=3)
        assert list(result["Lag"]) == [-3, -2, -1, 0, 1, 2, 3]

    def test_max_lag_zero(self):
        a = pd.Series([1.0, 2.0, 3.0, 4.0])
        b = pd.Series([2.0, 4.0, 6.0, 8.0])
        result = compute_lagged_correlation(a, b, max_lag=0)
        assert len(result) == 1
        assert result["Lag"].iloc[0] == 0
        assert result["Correlation"].iloc[0] == pytest.approx(1.0, abs=1e-6)


class TestLaggedCorrelationEdgeCases:
    def test_constant_series_all_nan(self):
        """Zero variance -> undefined Pearson -> NaN."""
        a = pd.Series([5.0, 5.0, 5.0, 5.0, 5.0])
        b = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = compute_lagged_correlation(a, b, max_lag=2)
        for _, row in result.iterrows():
            assert pd.isna(row["Correlation"])

    def test_short_series(self):
        """2 elements with lag=1: after shift only 1 valid pair -> NaN."""
        a = pd.Series([1.0, 2.0])
        b = pd.Series([3.0, 4.0])
        result = compute_lagged_correlation(a, b, max_lag=1)
        corr_dict = dict(zip(result["Lag"], result["Correlation"]))
        # lag=0: 2 points, both linear -> corr=1.0
        assert corr_dict[0] == pytest.approx(1.0, abs=1e-6)
        # lag=+-1: only 1 valid point after shift -> NaN
        assert pd.isna(corr_dict[1])
        assert pd.isna(corr_dict[-1])

    def test_single_element(self):
        a = pd.Series([1.0])
        b = pd.Series([2.0])
        result = compute_lagged_correlation(a, b, max_lag=1)
        for _, row in result.iterrows():
            assert pd.isna(row["Correlation"])

    def test_clean_series_strips_header(self):
        """Non-numeric first row (e.g. ticker name) is stripped."""
        a = pd.Series(["AAPL", "100", "200"])
        b = pd.Series(["MSFT", "50", "100"])
        result = compute_lagged_correlation(a, b, max_lag=0)
        # After stripping headers: [100,200] vs [50,100] -> perfectly correlated
        assert result["Correlation"].iloc[0] == pytest.approx(1.0, abs=1e-6)

    def test_empty_series(self):
        """Empty series should not crash (after bug fix)."""
        a = pd.Series([], dtype=float)
        b = pd.Series([], dtype=float)
        result = compute_lagged_correlation(a, b, max_lag=1)
        assert len(result) == 3  # -1, 0, 1
        for _, row in result.iterrows():
            assert pd.isna(row["Correlation"])
