import numpy as np
import pandas as pd
import pytest

from analysis.spread import calculate_zscore


class TestZScoreGlobal:
    def test_textbook_values(self, textbook_series):
        """[2,4,4,4,5,5,7,9] -> mean=5, std=2.13809 (ddof=1)."""
        result = calculate_zscore(textbook_series, window=None)
        mean = 5.0
        std = textbook_series.std()  # ddof=1 by default
        expected = [(v - mean) / std for v in textbook_series]
        for actual, exp in zip(result.tolist(), expected):
            assert actual == pytest.approx(exp, abs=1e-6)

    def test_mean_of_zscores_is_zero(self, textbook_series):
        result = calculate_zscore(textbook_series, window=None)
        assert result.mean() == pytest.approx(0.0, abs=1e-10)

    def test_std_of_zscores_is_one(self, textbook_series):
        result = calculate_zscore(textbook_series, window=None)
        assert result.std() == pytest.approx(1.0, abs=1e-10)

    def test_constant_series_all_nan(self, constant_series):
        """std=0 -> _safe_divisor returns NaN -> all z-scores are NaN."""
        result = calculate_zscore(constant_series, window=None)
        assert all(pd.isna(result))

    def test_single_element_nan(self):
        """std(ddof=1) of a single element is NaN."""
        result = calculate_zscore(pd.Series([42.0]), window=None)
        assert all(pd.isna(result))

    def test_two_elements(self):
        """Smallest valid case: [3,7] -> mean=5, std=2*sqrt(2)/sqrt(1)? No.
        std(ddof=1) of [3,7] = sqrt(((3-5)^2+(7-5)^2)/1) = sqrt(8) = 2.8284.
        z = [-0.7071, 0.7071]"""
        data = pd.Series([3.0, 7.0])
        result = calculate_zscore(data, window=None)
        expected = [-1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]
        for actual, exp in zip(result.tolist(), expected):
            assert actual == pytest.approx(exp, abs=1e-4)

    def test_with_nan_values(self):
        """NaN positions stay NaN; valid positions use mean/std of valid data."""
        data = pd.Series([1.0, np.nan, 3.0, 4.0, 5.0])
        result = calculate_zscore(data, window=None)
        # pandas mean/std skip NaN by default
        valid = data.dropna()
        mean = valid.mean()  # (1+3+4+5)/4 = 3.25
        std = valid.std()    # ddof=1
        assert np.isnan(result.iloc[1])
        assert result.iloc[0] == pytest.approx((1.0 - mean) / std, abs=1e-6)
        assert result.iloc[2] == pytest.approx((3.0 - mean) / std, abs=1e-6)

    def test_all_nan(self):
        result = calculate_zscore(pd.Series([np.nan, np.nan, np.nan]), window=None)
        assert all(pd.isna(result))

    def test_empty_series(self):
        result = calculate_zscore(pd.Series([], dtype=float), window=None)
        assert len(result) == 0


class TestZScoreRolling:
    def test_linear_ramp_all_ones(self):
        """For [1..10] with window=3, each point is 1 std above rolling mean.
        window=[k, k+1, k+2]: mean=k+1, std=1 (ddof=1), z=(k+2-(k+1))/1=1.0"""
        data = pd.Series(range(1, 11), dtype=float)
        result = calculate_zscore(data, window=3)
        # First 2 are NaN (not enough data for rolling)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        for i in range(2, 10):
            assert result.iloc[i] == pytest.approx(1.0, abs=1e-6)

    def test_window_larger_than_series(self):
        data = pd.Series([1.0, 2.0, 3.0])
        result = calculate_zscore(data, window=10)
        assert all(pd.isna(result))

    def test_nonuniform_data(self):
        """Hand-computed rolling z-scores for [10,12,8,15,11,9,14] window=3."""
        data = pd.Series([10.0, 12.0, 8.0, 15.0, 11.0, 9.0, 14.0])
        result = calculate_zscore(data, window=3)

        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])

        # Index 2: window=[10,12,8], mean=10, std=2.0, z=(8-10)/2 = -1.0
        assert result.iloc[2] == pytest.approx(-1.0, abs=1e-4)

        # Index 3: window=[12,8,15], mean=11.6667, std=3.5119, z=(15-11.6667)/3.5119 = 0.9492
        assert result.iloc[3] == pytest.approx(0.9492, abs=1e-3)

        # Index 4: window=[8,15,11], mean=11.3333, std=3.5119, z=(11-11.3333)/3.5119 = -0.0950
        assert result.iloc[4] == pytest.approx(-0.0950, abs=1e-3)

        # Index 5: window=[15,11,9], mean=11.6667, std=3.0551, z=(9-11.6667)/3.0551 = -0.8729
        assert result.iloc[5] == pytest.approx(-0.8729, abs=1e-3)

        # Index 6: window=[11,9,14], mean=11.3333, std=2.5166, z=(14-11.3333)/2.5166 = 1.0596
        assert result.iloc[6] == pytest.approx(1.0596, abs=1e-3)
