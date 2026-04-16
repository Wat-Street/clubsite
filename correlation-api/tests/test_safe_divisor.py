import numpy as np
import pandas as pd
import pytest

from analysis.spread import _safe_divisor


class TestSafeDivisorScalar:
    def test_nonzero_passthrough(self):
        assert _safe_divisor(5.0) == 5.0

    def test_zero_replaced_with_nan(self):
        assert np.isnan(_safe_divisor(0.0))

    def test_near_zero_below_tolerance(self):
        assert np.isnan(_safe_divisor(1e-13))

    def test_negative_near_zero_below_tolerance(self):
        assert np.isnan(_safe_divisor(-1e-13))

    def test_at_tolerance_boundary_kept(self):
        """Values exactly at the tolerance threshold (1e-12) are kept."""
        result = _safe_divisor(1e-12)
        assert result == 1e-12

    def test_nan_input(self):
        # abs(nan) < tol is False, so nan passes through as-is
        result = _safe_divisor(np.nan)
        assert np.isnan(result)


class TestSafeDivisorSeries:
    def test_mixed_values(self):
        s = pd.Series([1.0, 0.0, 3.0, -1e-13, 5.0])
        result = _safe_divisor(s)
        assert result.iloc[0] == 1.0
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == 3.0
        assert np.isnan(result.iloc[3])
        assert result.iloc[4] == 5.0

    def test_negative_near_zero_uses_abs(self):
        s = pd.Series([-1e-13, -1e-11])
        result = _safe_divisor(s)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == pytest.approx(-1e-11)
