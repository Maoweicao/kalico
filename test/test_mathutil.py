# Tests for the math helper functions
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import pytest

from klippy.mathutil import (
    coordinate_descent,
    gaussian_solve,
    mat_mat_mul,
    mat_mul_transp,
    mat_transp,
    matrix_add,
    matrix_cross,
    matrix_dot,
    matrix_magsq,
    matrix_mul,
    matrix_sub,
    pseudo_inverse,
    safe_float,
    solve_linear_equations,
    trilateration,
)

pytestmark = pytest.mark.unit

######################################################################
# safe_float
######################################################################


def test_safe_float():
    assert safe_float("1.5") == 1.5
    assert safe_float("-2") == -2.0


def test_safe_float_rejects_nan():
    with pytest.raises(ValueError):
        safe_float("nan")


def test_safe_float_rejects_inf():
    with pytest.raises(ValueError):
        safe_float("inf")
    with pytest.raises(ValueError):
        safe_float("-inf")


def test_safe_float_rejects_a_non_number():
    with pytest.raises(ValueError):
        safe_float("abc")


######################################################################
# Vector helpers
######################################################################


def test_matrix_add():
    assert matrix_add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]


def test_matrix_sub():
    assert matrix_sub([4, 5, 6], [1, 2, 3]) == [3, 3, 3]


def test_matrix_mul():
    assert matrix_mul([1, 2, 3], 2.0) == [2.0, 4.0, 6.0]


def test_matrix_dot():
    assert matrix_dot([1, 2, 3], [4, 5, 6]) == 32.0


def test_matrix_magsq():
    assert matrix_magsq([1, 2, 3]) == 14.0


def test_matrix_cross():
    assert matrix_cross([1, 0, 0], [0, 1, 0]) == [0, 0, 1]
    assert matrix_cross([0, 1, 0], [1, 0, 0]) == [0, 0, -1]


def test_matrix_cross_is_orthogonal():
    a = [1.0, 2.0, 3.0]
    b = [-2.0, 0.5, 4.0]
    assert matrix_dot(matrix_cross(a, b), a) == pytest.approx(0.0)
    assert matrix_dot(matrix_cross(a, b), b) == pytest.approx(0.0)


######################################################################
# Matrix helpers
######################################################################


def test_mat_transp():
    assert mat_transp([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_mat_mat_mul():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    assert mat_mat_mul(a, b) == [[19, 22], [43, 50]]


def test_mat_mat_mul_with_mismatched_shapes():
    # A 1x2 matrix cannot be multiplied with a 3x1 matrix
    assert mat_mat_mul([[1, 2]], [[1], [2], [3]]) is None


def test_mat_mul_transp_matches_the_generic_product():
    a = [[1.0, 2.0], [3.0, 4.0]]
    assert mat_mul_transp(a) == mat_mat_mul(a, mat_transp(a))


def test_mat_mul_transp_is_symmetric():
    a = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    res = mat_mul_transp(a)
    for i in range(len(res)):
        for j in range(len(res)):
            assert res[i][j] == pytest.approx(res[j][i])


######################################################################
# Linear algebra
######################################################################


def test_gaussian_solve():
    # 2x + y = 5, x + 3y = 10  ->  x = 1, y = 3
    a = [[2.0, 1.0], [1.0, 3.0]]
    rhs = [[5.0], [10.0]]
    res = gaussian_solve(a, rhs)
    assert res[0][0] == pytest.approx(1.0)
    assert res[1][0] == pytest.approx(3.0)


def test_gaussian_solve_of_a_singular_matrix():
    a = [[1.0, 2.0], [2.0, 4.0]]
    rhs = [[1.0], [2.0]]
    assert gaussian_solve(a, rhs) is None


def test_gaussian_solve_of_a_singular_matrix_underdetermined():
    a = [[1.0, 2.0], [2.0, 4.0]]
    rhs = [[1.0], [2.0]]
    res = gaussian_solve(a, rhs, allow_underdetermined=True)
    assert res is not None


def test_pseudo_inverse_of_a_square_matrix():
    m = [[2.0, 0.0], [0.0, 4.0]]
    inv = pseudo_inverse(m)
    assert inv[0][0] == pytest.approx(0.5)
    assert inv[1][1] == pytest.approx(0.25)


def test_pseudo_inverse_reconstructs_the_original():
    m = [[1.0, 2.0], [3.0, 4.0]]
    inv = pseudo_inverse(m)
    product = mat_mat_mul(inv, m)
    assert product[0][0] == pytest.approx(1.0, abs=1e-9)
    assert product[0][1] == pytest.approx(0.0, abs=1e-9)
    assert product[1][0] == pytest.approx(0.0, abs=1e-9)
    assert product[1][1] == pytest.approx(1.0, abs=1e-9)


def test_solve_linear_equations_recovers_a_known_solution():
    # x + y = 2, y + z = 3, x + z = 5  ->  x = 2, y = 0, z = 3
    eqs = [[1.0, 1.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, 1.0]]
    ans = [[2.0], [3.0], [5.0]]
    res = solve_linear_equations(eqs, ans)
    assert res[0][0] == pytest.approx(2.0)
    assert res[1][0] == pytest.approx(0.0)
    assert res[2][0] == pytest.approx(3.0)


def test_solve_linear_equations_of_a_least_squares_problem():
    # An over determined system - the result is the best fit
    eqs = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    ans = [[1.0], [1.0], [2.0]]
    res = solve_linear_equations(eqs, ans)
    assert res[0][0] == pytest.approx(1.0)
    assert res[1][0] == pytest.approx(1.0)


######################################################################
# Trilateration
######################################################################


def test_trilateration_finds_a_known_point():
    point = [1.0, 2.0, 3.0]
    spheres = [
        [0.0, 0.0, 0.0],
        [10.0, 0.0, 0.0],
        [0.0, 10.0, 0.0],
    ]
    radius2 = [
        sum((s - p) ** 2 for s, p in zip(sphere, point)) for sphere in spheres
    ]
    res = trilateration(spheres, radius2)
    assert res[0] == pytest.approx(point[0], abs=1e-6)
    assert res[1] == pytest.approx(point[1], abs=1e-6)
    # The algorithm always reports the solution with a negative z
    assert res[2] == pytest.approx(-point[2], abs=1e-6)


######################################################################
# Coordinate descent
######################################################################


def test_coordinate_descent_finds_the_minimum_of_a_quadratic():
    # (x - 3)^2 + (y + 1)^2
    def error_func(params):
        return (params["x"] - 3.0) ** 2 + (params["y"] + 1.0) ** 2

    res = coordinate_descent(["x", "y"], {"x": 0.0, "y": 0.0}, error_func)
    assert res["x"] == pytest.approx(3.0, abs=0.01)
    assert res["y"] == pytest.approx(-1.0, abs=0.01)


def test_coordinate_descent_does_not_modify_the_input():
    def error_func(params):
        return params["x"] ** 2

    params = {"x": 1.0}
    coordinate_descent(["x"], params, error_func)
    assert params == {"x": 1.0}


def test_coordinate_descent_keeps_an_unrelated_parameter():
    def error_func(params):
        return params["x"] ** 2

    res = coordinate_descent(["x"], {"x": 1.0, "other": 7.0}, error_func)
    assert res["other"] == 7.0


def test_coordinate_descent_of_a_flat_function():
    def error_func(params):
        return 1.0

    res = coordinate_descent(["x"], {"x": 1.0}, error_func)
    assert res["x"] == pytest.approx(1.0, abs=0.5)
