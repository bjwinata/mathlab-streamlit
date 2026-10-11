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
                     linear_inequality, logarithm, number_line, parabola)
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


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, func in tests:
        func()
        print("pass", name)
    print(f"{len(tests)} tests passed")
