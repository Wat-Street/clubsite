import numpy as np
import pandas as pd
import pytest

from analysis.spread import (
    calculate_price_difference_spread,
    calculate_ratio_spread,
    calculate_log_ratio_spread,
)


class TestPriceDifferenceSpread:
    def test_basic(self):
        a = pd.Series([100.0, 200.0, 150.0])
        b = pd.Series([90.0, 180.0, 160.0])
        result = calculate_price_difference_spread(a, b)
        expected = [10.0, 20.0, -10.0]
        assert list(result) == expected

    def test_identical_series_gives_zero(self):
        a = pd.Series([10.0, 20.0, 30.0])
        result = calculate_price_difference_spread(a, a)
        assert all(result == 0.0)


class TestRatioSpread:
    def test_basic(self):
        a = pd.Series([10.0, 20.0, 30.0])
        b = pd.Series([5.0, 10.0, 15.0])
        result = calculate_ratio_spread(a, b)
        assert list(result) == [2.0, 2.0, 2.0]

    def test_division_by_zero_gives_nan(self):
        a = pd.Series([10.0, 20.0, 30.0])
        b = pd.Series([5.0, 0.0, 10.0])
        result = calculate_ratio_spread(a, b)
        assert result.iloc[0] == 2.0
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == 3.0

    def test_negative_denominator(self):
        a = pd.Series([10.0, 20.0])
        b = pd.Series([-5.0, 10.0])
        result = calculate_ratio_spread(a, b)
        assert result.iloc[0] == pytest.approx(-2.0)
        assert result.iloc[1] == pytest.approx(2.0)


class TestLogRatioSpread:
    def test_basic(self):
        a = pd.Series([10.0, 20.0, 30.0])
        b = pd.Series([5.0, 10.0, 15.0])
        result = calculate_log_ratio_spread(a, b)
        expected = np.log(2.0)
        for val in result:
            assert val == pytest.approx(expected, abs=1e-10)

    def test_negative_ratio_becomes_nan(self):
        a = pd.Series([-1.0, 2.0, 3.0])
        b = pd.Series([1.0, 1.0, 1.0])
        result = calculate_log_ratio_spread(a, b)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == pytest.approx(np.log(2.0))
        assert result.iloc[2] == pytest.approx(np.log(3.0))

    def test_division_by_zero(self):
        a = pd.Series([10.0, 20.0])
        b = pd.Series([0.0, 10.0])
        result = calculate_log_ratio_spread(a, b)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == pytest.approx(np.log(2.0))

    def test_ratio_of_one_gives_zero(self):
        a = pd.Series([5.0, 5.0])
        b = pd.Series([5.0, 5.0])
        result = calculate_log_ratio_spread(a, b)
        for val in result:
            assert val == pytest.approx(0.0, abs=1e-10)

    def test_preserves_index(self):
        idx = pd.Index([10, 20, 30])
        a = pd.Series([100.0, 200.0, 300.0], index=idx)
        b = pd.Series([50.0, 100.0, 150.0], index=idx)
        result = calculate_log_ratio_spread(a, b)
        assert list(result.index) == [10, 20, 30]
