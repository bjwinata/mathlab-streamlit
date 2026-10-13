"""Checks of the maths behind each project.

    pytest tests            (if pytest is installed)
    python tests/test_logic.py
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conftest  # noqa: F401,E402  (sets up the import path / Streamlit stub)

import numpy as np  # noqa: E402

from mathlab import (abs_inequality, completing_square, compound_interest,  # noqa: E402
                     conic_sections, linear_inequality, logarithm, number_line,
                     parabola, polar_coordinates, vector_operation)
from mathlab.safe_math import parse_equation  # noqa: E402
from mathlab.formatting import fmt, poly_latex, vertex_form_latex  # noqa: E402


def test_fmt():
    assert fmt(2.0) == "2"
    assert fmt(3.5000) == "3.5"
    assert fmt(-4.0) == "-4"
    assert fmt(-0.00001) == "0"
    assert fmt(1e-12) == "0"


def test_poly_latex():
    assert poly_latex(1, 0, 0) == "x^{2}"
    assert poly_latex(-1, 2, -3) == "-x^{2} + 2x - 3"
    assert poly_latex(2, 0, 5) == "2x^{2} + 5"
    assert vertex_form_latex(1, -3, -4) == "y = (x + 3)^{2} - 4"


def test_parabola_properties():
    p = parabola.analyze(1, 6, 5)
    assert (p.vertex_x, p.vertex_y) == (-3, -4)
    assert p.roots == [-5, -1] and p.kind == "two"
    assert parabola.analyze(1, -6, 9).kind == "one"
    assert parabola.analyze(1, 0, 1).kind == "complex"
    props = dict(parabola.properties(p))
    assert props["Focus"] == "(-3, -3.75)"
    assert props["Directrix"] == "y = -4.25"
    assert props["Range"] == "y ≥ -4"


def test_completing_the_square_is_equivalent():
    rng = random.Random(1)
    for _ in range(200):
        a = rng.choice([-3, -1, -0.5, 0.5, 1, 2, 4])
        b, c = rng.randint(-9, 9), rng.randint(-9, 9)
        steps, h, k = completing_square.solve_steps(a, b, c)
        assert len(steps) == 6
        for x in (-2.5, 0, 1.5, 7):
            assert math.isclose(a * (x - h) ** 2 + k, a * x * x + b * x + c,
                                abs_tol=1e-9)


def test_linear_inequality():
    assert linear_inequality.find_intersection(2, 1, -1, 7) == (2, 5)
    assert linear_inequality.find_intersection(1, 0, 1, 3) is None
    assert linear_inequality.choose_graph_size(None) == (-10, 10, -10, 10)
    assert linear_inequality.holds(5, 3, ">") and not linear_inequality.holds(3, 3, ">")
    assert linear_inequality.holds(3, 3, ">=")


def test_absolute_value():
    assert abs_inequality.satisfies(5, 2 * abs(3 - 1) - 1, ">=")
    assert abs_inequality.satisfies(2, 3, "<=") and not abs_inequality.satisfies(4, 3, "<=")
    assert abs_inequality.get_graph_range(0, 0, 0, 2) == (-5, 5, -5, 7)
    assert abs_inequality.inequality_latex(2, 3, -1, ">=") == r"y \geq 2|x - 3| - 1"


def test_number_line():
    x = np.array([2.0, 3.0, 7.0, 8.0])
    assert list(number_line.combined_solution(x, ">", 2, "<=", 7, "AND")) == [False, True, True, False]
    assert list(number_line.combined_solution(x, "<", 2, ">", 7, "OR")) == [False, False, False, True]
    assert number_line.axis_limits(2, 6) == (-1, 9)
    assert number_line.axis_limits(-2.5, 3) == (-6, 6)
    runs = number_line.true_runs(np.arange(10), np.arange(10) % 5 < 2)
    assert runs == [(0, 1), (5, 6)]


def test_compound_interest():
    amount = float(compound_interest.calculate_amount(10000, 0.06, 10, "Monthly"))
    assert round(amount, 2) == 18193.97
    results = compound_interest.calculate_all_methods(10000, 0.06, 10)
    order = ["Annual", "Quarterly", "Monthly", "Daily", "Continuous"]
    assert [results[m] for m in order] == sorted(results[m] for m in order)
    assert math.isclose(results["Continuous"], 10000 * math.exp(0.6))
    for method in order:
        assert compound_interest.solution_steps(10000, 0.06, 10, method)


def test_logarithm_inverse_round_trip():
    for base, a, h, k in [(2, 1, 0, 0), (3, -2, 1, 2), (0.5, 2, -3, -1)]:
        x = np.array([-2.0, 0.0, 1.5, 3.0])
        inverse = logarithm.changed_log_inverse_values(x, a, h, k, base)
        back = logarithm.changed_log_values(inverse, a, h, k, base)
        assert np.allclose(back, x)


def test_logarithm_domain_and_validity():
    assert not logarithm.is_valid_base(1) and not logarithm.is_valid_base(-2)
    y = logarithm.changed_log_values(np.array([-1.0, 0.0, 1.0, 3.0]), 1, 1, 0, 2)
    assert np.isnan(y[:3]).all() and math.isclose(y[3], 1.0)
    assert np.isnan(logarithm.changed_log_values(np.array([5.0]), 0, 0, 0, 2)).all()


# ----------------------------------------------------------------------
# Safe equation parser (Polar page)
# ----------------------------------------------------------------------

def _refused(text, variables=("theta", "r", "x", "y")):
    try:
        parse_equation(text, set(variables))
    except ValueError:
        return True
    return False


def test_safe_parser_refuses_code():
    for attack in ["__import__('os').system('echo hi')", "().__class__",
                   "open('/etc/passwd')", "lambda: 1", "theta.real", "'text'",
                   "np.sin(theta)", "[1, 2]", "x; y", "exec('1')", "z + 1",
                   "x" * 200, "1e999", "sin", "sin(1, 2)"]:
        assert _refused(attack), attack


def test_safe_parser_values_match_numpy():
    theta = np.linspace(0, 2 * np.pi, 50)
    cases = {"2*cos(3*theta)": 2 * np.cos(3 * theta),
             "2 + 2*cos(theta)": 2 + 2 * np.cos(theta),
             "0.2*exp(0.15*theta)": 0.2 * np.exp(0.15 * theta),
             "theta^2": theta ** 2,          # ^ works like **
             "-sqrt(abs(theta)) + pi": -np.sqrt(np.abs(theta)) + np.pi}
    for text, expected in cases.items():
        value = parse_equation(text, {"theta"}).evaluate(theta=theta)
        assert np.allclose(np.broadcast_to(value, theta.shape), expected), text


def test_safe_parser_mode_and_size_limits():
    assert _refused("r + 1", {"theta"}) and _refused("theta", {"x", "y"})
    huge = parse_equation("9**9**9**9", {"theta"})   # evaluating it is harmless...
    assert np.isinf(huge.evaluate(theta=np.array([1.0])))
    try:                                             # ...and symbolic work refuses it
        huge.to_sympy()
        assert False, "should have been refused"
    except ValueError:
        pass


# ----------------------------------------------------------------------
# Polar coordinates
# ----------------------------------------------------------------------

def test_polar_area_estimates():
    area = lambda eq: float(next(l for l in polar_coordinates.analyze(
        "Area estimate", eq, polar_coordinates.MODE_EXPLICIT, 0, 360, "Degrees",
        1800).splitlines() if l.startswith("A ≈")).split()[2])
    assert math.isclose(area("2"), 4 * math.pi, rel_tol=1e-6)
    assert math.isclose(area("2 + 2*cos(theta)"), 6 * math.pi, rel_tol=1e-6)
    assert math.isclose(area("2*cos(3*theta)"), 2 * math.pi, rel_tol=1e-6)


def test_polar_implicit_grid_and_errors():
    eq = parse_equation("x**2 + y**2 - 4", {"x", "y"})
    x, y, values = polar_coordinates.implicit_grid(eq, polar_coordinates.MODE_CARTESIAN, 3, 101)
    assert values.shape == (101, 101) and values.min() < 0 < values.max()
    try:
        polar_coordinates.angle_range_radians(90, 10, "Degrees")
        assert False
    except ValueError:
        pass


# ----------------------------------------------------------------------
# Vector operation
# ----------------------------------------------------------------------

def test_vectors():
    a, b = (3, 2, 1), (1, 3, 2)
    cross = vector_operation.cross_product_3d(a, b)
    assert cross == (1, -5, 7)
    assert vector_operation.dot_product(cross, a) == 0 == vector_operation.dot_product(cross, b)
    assert vector_operation.add_vectors(a, b) == (4, 5, 3)
    assert vector_operation.subtract_vectors(a, b) == (2, -1, -1)
    result, lines = vector_operation.operate_2d((3, 2), (1, 3), "Dot product (A · B)")
    assert result is None and lines[0] == "A · B = 9" and "37.87" in lines[1]
    assert "undefined" in vector_operation.angle_text((0, 0), (1, 1))
    assert "out of the screen" in vector_operation.operate_2d((3, 2), (1, 3), "Cross product (A × B)")[1][2]


# ----------------------------------------------------------------------
# Conic sections
# ----------------------------------------------------------------------

def test_conic_equations():
    assert conic_sections.circle_data(0, 0, 4)["equation"] == "x² + y² = 16"
    assert conic_sections.circle_data(2, -3, 5)["expanded"] == "x² + y² - 4x + 6y - 12 = 0"
    assert conic_sections.parabola_data(0, 0, 1, "Vertical")["equation"] == "x² = 4y"
    assert conic_sections.parabola_data(1, 2, -0.25, "Horizontal")["expanded"] == "y² - 4y + x + 3 = 0"
    assert conic_sections.ellipse_data(1, -2, 3, 5, "Vertical")["expanded"] == "9x² + 25y² - 18x + 100y - 116 = 0"
    assert conic_sections.hyperbola_data(2, 1, 3, 2, "Vertical")["expanded"] == "-9x² + 4y² + 36x - 8y - 68 = 0"


def test_conic_properties_and_validation():
    props = conic_sections.parabola_data(0, 0, 1, "Vertical")["properties"]
    assert "Focus: (0, 1)" in props and "Directrix: y = -1" in props
    assert "Eccentricity: 0.866" in conic_sections.ellipse_data(0, 0, 4, 2, "Horizontal")["properties"]
    for bad in (lambda: conic_sections.circle_data(0, 0, -1),
                lambda: conic_sections.parabola_data(0, 0, 0, "Vertical"),
                lambda: conic_sections.ellipse_data(0, 0, 0, 2, "Horizontal"),
                lambda: conic_sections.hyperbola_data(0, 0, 3, -1, "Vertical")):
        try:
            bad()
            assert False
        except ValueError:
            pass


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, func in tests:
        func()
        print("pass", name)
    print(f"{len(tests)} tests passed")
