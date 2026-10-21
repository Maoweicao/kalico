# Tests for the calibration geometry helpers
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math

import numpy as np
import pytest

from klippy.extras.quad_gantry_level import QuadGantryLevel
from klippy.extras.skew_correction import PrinterSkew, calc_skew_factor
from klippy.extras.z_tilt_ng import intersect_3_planes, params_to_normal_form

pytestmark = pytest.mark.unit
######################################################################
# z_tilt_ng
######################################################################


def test_params_to_normal_form():
    params = {"x_adjust": 0.1, "y_adjust": 0.2, "z_adjust": 0.3}
    offsets = [0.0, 0.0, 0.0]
    res = params_to_normal_form(params, offsets)
    # The normal of the plane is the cross product of the x and y axes
    assert res[0] == pytest.approx(-0.1)
    assert res[1] == pytest.approx(-0.2)
    assert res[2] == pytest.approx(1.0)
    assert res[3] == pytest.approx(0.3)


def test_params_to_normal_form_with_offsets():
    params = {"x_adjust": 0.5, "y_adjust": 0.0, "z_adjust": 1.0}
    without = params_to_normal_form(params, [0.0, 0.0, 0.0])
    with_offsets = params_to_normal_form(params, [1.0, 2.0, 0.0])
    # The x and y offsets move the plane
    assert with_offsets[3] != pytest.approx(without[3])
    assert with_offsets[3] == pytest.approx(0.5)


def test_intersect_3_planes():
    # Three planes that all pass through the point (1, 2, 3)
    p1 = [1.0, 0.0, 0.0, 1.0]
    p2 = [0.0, 1.0, 0.0, 2.0]
    p3 = [0.0, 0.0, 1.0, 3.0]
    sol = intersect_3_planes(p1, p2, p3)
    assert sol[0] == pytest.approx(1.0)
    assert sol[1] == pytest.approx(2.0)
    assert sol[2] == pytest.approx(3.0)


def test_intersect_3_planes_of_parallel_planes():
    # Parallel planes have no intersection
    p1 = [1.0, 0.0, 0.0, 1.0]
    p2 = [1.0, 0.0, 0.0, 2.0]
    p3 = [0.0, 1.0, 0.0, 3.0]
    with pytest.raises(np.linalg.LinAlgError):
        intersect_3_planes(p1, p2, p3)


######################################################################
# quad_gantry_level
######################################################################


def _make_qgl():
    qgl = object.__new__(QuadGantryLevel)
    return qgl


def test_linefit():
    qgl = _make_qgl()
    m, b = qgl.linefit((0.0, 1.0), (2.0, 3.0))
    assert m == pytest.approx(1.0)
    assert b == pytest.approx(1.0)


def test_linefit_of_a_horizontal_line():
    qgl = _make_qgl()
    # A horizontal line has a slope of zero
    m, b = qgl.linefit((0.0, 2.0), (5.0, 2.0))
    assert m == 0
    assert b == pytest.approx(2.0)


def test_linefit_of_a_vertical_line():
    qgl = _make_qgl()
    # A vertical line has an infinite slope - the special case avoids the
    # division by zero
    with pytest.raises(ZeroDivisionError):
        qgl.linefit((1.0, 0.0), (1.0, 2.0))


def test_plot():
    qgl = _make_qgl()
    f = qgl.linefit((0.0, 1.0), (2.0, 3.0))
    assert qgl.plot(f, 4.0) == pytest.approx(5.0)


def test_plot_of_a_horizontal_line():
    qgl = _make_qgl()
    f = qgl.linefit((0.0, 2.0), (5.0, 2.0))
    assert qgl.plot(f, 100.0) == pytest.approx(2.0)


######################################################################
# skew_correction
######################################################################


def test_calc_skew_factor_of_a_rectangle():
    # The measurement of a rectangle: the diagonals and one side
    side = 100.0
    diagonal = side * math.sqrt(2)
    assert calc_skew_factor(diagonal, diagonal, side) == pytest.approx(
        0.0, abs=1e-6
    )


def test_calc_skew_factor_of_a_skewed_shape():
    # One diagonal is longer than the other - the shape is skewed
    factor = calc_skew_factor(141.42, 145.0, 100.0)
    assert factor != pytest.approx(0.0)
    assert math.isfinite(factor)


def test_calc_skew_factor_of_a_degenerate_measurement():
    # A measurement where the diagonals are as long as the side has no
    # solution - the calculation divides by zero
    with pytest.raises(ZeroDivisionError):
        calc_skew_factor(100.0, 100.0, 100.0)


def _make_skew(xy=0.0, xz=0.0, yz=0.0):
    skew = object.__new__(PrinterSkew)
    skew.xy_factor = xy
    skew.xz_factor = xz
    skew.yz_factor = yz
    return skew


def test_calc_skew_without_a_skew():
    skew = _make_skew()
    assert skew.calc_skew([1.0, 2.0, 3.0]) == [1.0, 2.0, 3.0]
    assert skew.calc_unskew([1.0, 2.0, 3.0]) == [1.0, 2.0, 3.0]


def test_calc_skew_with_an_xy_factor():
    skew = _make_skew(xy=0.1)
    res = skew.calc_skew([1.0, 2.0, 0.0])
    assert res[0] == pytest.approx(1.0 - 2.0 * 0.1)
    assert res[1] == pytest.approx(2.0)


def test_calc_skew_with_a_yz_factor():
    skew = _make_skew(yz=0.1)
    res = skew.calc_skew([1.0, 2.0, 3.0])
    assert res[0] == pytest.approx(1.0)
    assert res[1] == pytest.approx(2.0 - 3.0 * 0.1)


def test_calc_unskew_with_an_xz_factor():
    skew = _make_skew(xz=0.1)
    res = skew.calc_unskew([1.0, 2.0, 3.0])
    assert res[0] == pytest.approx(1.0 + 3.0 * 0.1)
    assert res[1] == pytest.approx(2.0)


def test_calc_skew_and_calc_unskew_are_inverse():
    # The xy skew is inverted by the unskew transform
    skew = _make_skew(xy=0.1)
    pos = [1.0, 2.0, 0.0]
    skewed = skew.calc_skew(pos)
    assert skew.calc_unskew(skewed)[0] == pytest.approx(pos[0])
    assert skew.calc_unskew(skewed)[1] == pytest.approx(pos[1])
