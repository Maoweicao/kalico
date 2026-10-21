# Tests for the bed mesh interpolation
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pytest

from klippy.extras.bed_mesh import (
    ZMesh,
    constrain,
    isclose,
    lerp,
    parse_config_pair,
    within,
)

pytestmark = pytest.mark.unit

######################################################################
# The helper functions
######################################################################


def test_isclose():
    assert isclose(1.0, 1.0 + 1e-10) is True
    assert isclose(1.0, 1.1) is False


def test_within():
    # The coordinates are pairs
    assert within((5.0, 5.0), (0.0, 0.0), (10.0, 10.0)) is True
    assert within((11.0, 5.0), (0.0, 0.0), (10.0, 10.0)) is False
    assert within((-1.0, 5.0), (0.0, 0.0), (10.0, 10.0)) is False
    assert within((10.5, 5.0), (0.0, 0.0), (10.0, 10.0), 1.0) is True


def test_constrain():
    assert constrain(5.0, 0.0, 10.0) == 5.0
    assert constrain(-5.0, 0.0, 10.0) == 0.0
    assert constrain(15.0, 0.0, 10.0) == 10.0


def test_lerp():
    assert lerp(0.0, 10.0, 20.0) == pytest.approx(10.0)
    assert lerp(0.5, 10.0, 20.0) == pytest.approx(15.0)
    assert lerp(1.0, 10.0, 20.0) == pytest.approx(20.0)


def test_parse_config_pair():
    class _FakeConfig:
        error = Exception

        def getintlist(self, option, default=None):
            return [1, 2]

        def get(self, option, default=None):
            return "1, 2"

    config = _FakeConfig()
    pair = parse_config_pair(config, "x", 0, 0.0, 10.0)
    assert pair == [1, 2]


def test_parse_config_pair_of_a_single_value():
    class _FakeConfig:
        error = Exception

        def getintlist(self, option, default=None):
            return [3]

        def get(self, option, default=None):
            return "3"

    config = _FakeConfig()
    pair = parse_config_pair(config, "x", 0)
    assert pair == (3, 3)


######################################################################
# The mesh
######################################################################


def _make_params(algo="lagrange", x_count=3, y_count=3):
    # The "direct" algorithm uses the probed values without any
    # interpolation - the probe grid has to be the mesh grid
    pps = 0 if algo == "direct" else 1
    return {
        "min_x": 0.0,
        "max_x": 20.0,
        "min_y": 0.0,
        "max_y": 20.0,
        "algo": algo,
        "mesh_x_pps": pps,
        "mesh_y_pps": pps,
        "x_count": x_count,
        "y_count": y_count,
        "min_z": 0.0,
        "max_z": 0.05,
        "horizontal_move_z": 0.005,
        # The default of the "bicubic_tension" option
        "tension": 0.2,
    }


def _make_mesh(algo="lagrange"):
    mesh = ZMesh(_make_params(algo), "test")
    # A flat mesh - the matrix holds the probed values
    matrix = [
        [0.0] * mesh.mesh_params["x_count"]
        for _ in range(mesh.mesh_params["y_count"])
    ]
    mesh.build_mesh(matrix)
    return mesh


def _make_sloped_mesh(algo="lagrange", slope_x=0.01, slope_y=0.02):
    mesh = ZMesh(_make_params(algo), "test")
    matrix = []
    for pj in range(mesh.mesh_params["y_count"]):
        row = []
        for pi in range(mesh.mesh_params["x_count"]):
            x = mesh.get_x_coordinate(pi * mesh.x_mult)
            y = mesh.get_y_coordinate(pj * mesh.y_mult)
            row.append(slope_x * x + slope_y * y)
        matrix.append(row)
    mesh.build_mesh(matrix)
    return mesh


def test_an_empty_mesh_returns_zero():
    mesh = ZMesh(_make_params(), "test")
    assert mesh.calc_z(10.0, 10.0) == 0.0


def test_a_flat_mesh_returns_zero():
    mesh = _make_mesh()
    assert mesh.calc_z(0.0, 0.0) == pytest.approx(0.0)
    assert mesh.calc_z(10.0, 10.0) == pytest.approx(0.0)
    assert mesh.calc_z(20.0, 20.0) == pytest.approx(0.0)


@pytest.mark.parametrize("algo", ["lagrange", "bicubic", "direct"])
def test_a_sloped_mesh_interpolates(algo):
    mesh = _make_sloped_mesh(algo)
    # The mesh has a slope of 0.01 per x index and 0.02 per y index
    assert mesh.calc_z(0.0, 0.0) == pytest.approx(0.0, abs=1e-6)
    assert mesh.calc_z(10.0, 0.0) == pytest.approx(0.01 * 10, abs=1e-4)
    assert mesh.calc_z(0.0, 10.0) == pytest.approx(0.02 * 10, abs=1e-4)


@pytest.mark.parametrize("algo", ["lagrange", "bicubic", "direct"])
def test_the_probed_points_are_reproduced(algo):
    mesh = _make_sloped_mesh(algo)
    for pi in range(mesh.mesh_params["x_count"]):
        for pj in range(mesh.mesh_params["y_count"]):
            x = mesh.get_x_coordinate(pi * mesh.x_mult)
            y = mesh.get_y_coordinate(pj * mesh.y_mult)
            res = mesh.calc_z(x, y)
            assert res == pytest.approx(0.01 * x + 0.02 * y, abs=1e-6)


@pytest.mark.parametrize("algo", ["lagrange", "direct"])
def test_the_interpolated_points_are_exact_for_a_plane(algo):
    # The Lagrange interpolation reproduces a plane exactly
    mesh = _make_sloped_mesh(algo)
    for xidx in range(mesh.mesh_x_count):
        for yidx in range(mesh.mesh_y_count):
            x = mesh.get_x_coordinate(xidx)
            y = mesh.get_y_coordinate(yidx)
            res = mesh.calc_z(x, y)
            assert res == pytest.approx(0.01 * x + 0.02 * y, abs=1e-4)


def test_the_bicubic_interpolation_is_close_for_a_plane():
    # The cardinal spline derives the tangents from the tension - with
    # the default tension the values are close but not exact.  The border
    # of the mesh uses an approximate tangent as well.
    mesh = _make_sloped_mesh("bicubic")
    for xidx in range(mesh.mesh_x_count):
        for yidx in range(mesh.mesh_y_count):
            x = mesh.get_x_coordinate(xidx)
            y = mesh.get_y_coordinate(yidx)
            res = mesh.calc_z(x, y)
            assert res == pytest.approx(0.01 * x + 0.02 * y, abs=0.01)


def test_the_z_range_of_a_flat_mesh():
    mesh = _make_mesh()
    assert mesh.get_z_range() == (0.0, 0.0)


def test_the_z_average_of_a_flat_mesh():
    mesh = _make_mesh()
    assert mesh.get_z_average() == 0.0


def test_the_z_range_of_a_sloped_mesh():
    mesh = _make_sloped_mesh()
    z_min, z_max = mesh.get_z_range()
    assert z_min == pytest.approx(0.0)
    assert z_max > 0.0


def test_the_zero_reference_shifts_the_mesh():
    mesh = _make_sloped_mesh()
    before = mesh.calc_z(10.0, 10.0)
    mesh.set_zero_reference(10.0, 10.0)
    assert mesh.calc_z(10.0, 10.0) == pytest.approx(0.0, abs=1e-6)
    # The rest of the mesh is shifted by the same amount
    assert mesh.calc_z(0.0, 0.0) == pytest.approx(-before, abs=1e-4)


def test_the_mesh_offsets_shift_the_lookup():
    mesh = _make_sloped_mesh()
    before = mesh.calc_z(10.0, 0.0)
    mesh.set_mesh_offsets([10.0, 0.0])
    assert mesh.calc_z(0.0, 0.0) == pytest.approx(before, abs=1e-4)
