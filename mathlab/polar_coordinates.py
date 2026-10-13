"""Project Polar Coordinates - an interactive polar curve explorer.

Three equation types:
    Explicit            r = f(theta)
    Implicit polar      F(r, theta) = 0
    Cartesian implicit  F(x, y) = 0

Equations are read with ``safe_math`` (no eval), e.g.
    2*cos(3*theta)      r**2 - 4*cos(2*theta)      x**2 + y**2 - 4*x
"""

import math

import numpy as np
import sympy as sp
import streamlit as st
from matplotlib.figure import Figure

from .safe_math import (parse_equation, r_symbol, theta_symbol, x_symbol,
                        y_symbol)

MODE_EXPLICIT = "Explicit: r = f(theta)"
MODE_POLAR = "Implicit polar: F(r, theta) = 0"
MODE_CARTESIAN = "Cartesian implicit: F(x, y) = 0"
MODES = [MODE_EXPLICIT, MODE_POLAR, MODE_CARTESIAN]
ALLOWED_VARIABLES = {MODE_EXPLICIT: {"theta"}, MODE_POLAR: {"r", "theta"},
                     MODE_CARTESIAN: {"x", "y"}}

CURVE_COLOR = "#2463a6"
ANALYSES = ["Symmetry and key facts", "Cartesian conversion",
            "Derivative and tangent", "Area estimate"]

FAMILY_PRESETS = {
    "Circle / constant radius": (
        MODE_EXPLICIT, "2",
        "Try r = 2, or use 2*cos(theta) for a circle through the pole."),
    "Limaçon / cardioid": (
        MODE_EXPLICIT, "2 + 2*cos(theta)",
        "Change the two numbers in a + b*cos(theta)."),
    "Rose curve": (
        MODE_EXPLICIT, "2*cos(3*theta)",
        "Try 2*cos(4*theta) and compare the number of petals."),
    "Lemniscate (implicit)": (
        MODE_POLAR, "r**2 - 4*cos(2*theta)",
        "The graph shows points where this expression equals zero."),
    "Archimedean spiral": (
        MODE_EXPLICIT, "0.15*theta",
        "Change 0.15 to adjust how quickly the spiral grows."),
    "Logarithmic spiral": (
        MODE_EXPLICIT, "0.2*exp(0.15*theta)",
        "Change the growth rate inside exp(...)."),
    "Polar conic": (
        MODE_EXPLICIT, "2/(1 + 0.5*cos(theta))",
        "This example has eccentricity 0.5, so it is an ellipse-like conic."),
    "Custom equation": (
        MODE_EXPLICIT, "2 + cos(2*theta)",
        "Type your own supported equation."),
}

DEFAULTS = {
    "pol_display": "Beginner", "pol_family": "Rose curve",
    "pol_mode": MODE_EXPLICIT, "pol_equation": "2*cos(3*theta)",
    "pol_note": FAMILY_PRESETS["Rose curve"][2],
    "pol_start": 0.0, "pol_end": 360.0, "pol_units": "Degrees",
    "pol_grid": True, "pol_analysis_choice": ANALYSES[0],
    "pol_analysis_text": "Choose an analysis and click Analyze. "
                         "The graph remains above.",
    # advanced settings (kept even while the Advanced panel is hidden)
    "pol_res": 220, "pol_samples": 1800, "pol_limit": 6.0,
}


# ======================================================================
# MATH
# ======================================================================

def equation_hint(mode):
    if mode == MODE_EXPLICIT:
        return "Enter an expression in theta, such as 2*cos(3*theta)."
    if mode == MODE_POLAR:
        return "Enter F(r, theta) = 0 as an expression, such as r**2 - 4*cos(2*theta)."
    return "Enter F(x, y) = 0 as an expression, such as x**2 + y**2 - 4*x."


def angle_range_radians(start, end, units):
    if end <= start:
        raise ValueError("The ending angle must be larger than the starting angle.")
    if units == "Degrees":
        return math.radians(start), math.radians(end)
    return start, end


def _as_array(values, shape):
    """Constants evaluate to a single number; spread them over the grid."""
    values = np.broadcast_to(np.asarray(values, dtype=float), shape).astype(float)
    values[~np.isfinite(values)] = np.nan
    return values


def explicit_points(equation, start, end, samples):
    """Angles and radii for r = f(theta); undefined values become NaN."""
    angles = np.linspace(start, end, int(samples))
    radii = _as_array(equation.evaluate(theta=angles), angles.shape)
    radii[np.abs(radii) > 1e4] = np.nan
    if np.all(np.isnan(radii)):
        raise ValueError("This equation has no plottable values in the selected range.")
    return angles, radii


def implicit_grid(equation, mode, limit, resolution):
    """Values of F on a square grid; the curve is where F = 0."""
    axis = np.linspace(-limit, limit, int(resolution))
    x_grid, y_grid = np.meshgrid(axis, axis)
    if mode == MODE_POLAR:
        values = equation.evaluate(r=np.sqrt(x_grid ** 2 + y_grid ** 2),
                                   theta=np.arctan2(y_grid, x_grid))
    else:
        values = equation.evaluate(x=x_grid, y=y_grid)
    values = _as_array(values, x_grid.shape)
    if not np.any(np.isfinite(values)):
        raise ValueError("This equation has no usable values in the view.")
    return x_grid, y_grid, values


def make_figure(text, mode, start, end, units, grid, samples, limit, resolution):
    """Return the finished Matplotlib figure (raises ValueError on bad input)."""
    equation = parse_equation(text, ALLOWED_VARIABLES[mode])
    fig = Figure(figsize=(6.5, 6.0))

    if mode == MODE_EXPLICIT:
        a0, a1 = angle_range_radians(start, end, units)
        angles, radii = explicit_points(equation, a0, a1, samples)
        ax = fig.add_subplot(111, projection="polar")
        ax.plot(angles, radii, linewidth=2.2, color=CURVE_COLOR)
        if math.degrees(a1 - a0) < 360:
            ax.set_thetamin(math.degrees(a0))
            ax.set_thetamax(math.degrees(a1))
        ax.set_theta_zero_location("E")
        ax.set_theta_direction(1)
        ax.set_title("Polar graph", pad=18)
    else:
        x_grid, y_grid, values = implicit_grid(equation, mode, limit, resolution)
        ax = fig.add_subplot(111)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.axvline(0, color="gray", linewidth=0.7)
        if np.nanmin(values) <= 0 <= np.nanmax(values):
            ax.contour(x_grid, y_grid, values, levels=[0],
                       colors=[CURVE_COLOR], linewidths=2.0)
        else:
            ax.text(0.5, 0.5, "No points where F = 0\nin this view",
                    transform=ax.transAxes, ha="center", va="center")
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_title("Implicit curve on an x-y grid", pad=18)
    ax.grid(grid)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Analysis (SymPy)
# ----------------------------------------------------------------------

def analyze(choice, text, mode, start, end, units, samples):
    """Return the analysis as plain text (raises ValueError on bad input)."""
    equation = parse_equation(text, ALLOWED_VARIABLES[mode])
    expression = equation.to_sympy()
    if choice == "Cartesian conversion":
        return _analysis_cartesian(expression, mode)
    if choice == "Derivative and tangent":
        return _analysis_derivative(expression, mode)
    if choice == "Area estimate":
        return _analysis_area(equation, mode, start, end, units, samples)
    return _analysis_symmetry(expression, mode)


def _analysis_cartesian(expression, mode):
    if mode == MODE_EXPLICIT:
        x_expression = sp.simplify(expression * sp.cos(theta_symbol))
        y_expression = sp.simplify(expression * sp.sin(theta_symbol))
        return ("For an explicit polar curve r = f(theta):\n"
                f"x(theta) = {sp.sstr(x_expression)}\n"
                f"y(theta) = {sp.sstr(y_expression)}\n\n"
                "These equations describe the same curve parametrically. "
                "Eliminating theta may not produce a simple equation.")
    if mode == MODE_POLAR:
        substituted = sp.simplify(expression.subs({
            r_symbol: sp.sqrt(x_symbol ** 2 + y_symbol ** 2),
            theta_symbol: sp.atan2(y_symbol, x_symbol)}))
        return ("A useful substitution is r = sqrt(x^2 + y^2) and "
                "theta = atan2(y, x).\n"
                f"Substituted expression:\n{substituted}\n\n"
                "Check branch and domain restrictions: symbolic substitutions "
                "can change how an equation is represented.")
    polar_expression = sp.simplify(expression.subs({
        x_symbol: r_symbol * sp.cos(theta_symbol),
        y_symbol: r_symbol * sp.sin(theta_symbol)}))
    return ("Substitute x = r*cos(theta) and y = r*sin(theta):\n"
            f"F(r, theta) = {polar_expression}\n\n"
            "The curve is the set of points where this expression equals zero.")


def _analysis_derivative(expression, mode):
    if mode == MODE_EXPLICIT:
        derivative = sp.simplify(sp.diff(expression, theta_symbol))
        numerator = sp.simplify(derivative * sp.sin(theta_symbol)
                                + expression * sp.cos(theta_symbol))
        denominator = sp.simplify(derivative * sp.cos(theta_symbol)
                                  - expression * sp.sin(theta_symbol))
        return (f"r(theta) = {sp.sstr(expression)}\n"
                f"dr/dtheta = {sp.sstr(derivative)}\n\n"
                "Cartesian slope formula:\n"
                "(r' sin(theta) + r cos(theta)) /\n"
                "(r' cos(theta) - r sin(theta))\n\n"
                f"Numerator: {sp.sstr(numerator)}\n"
                f"Denominator: {sp.sstr(denominator)}\n\n"
                "A zero denominator may mean a vertical tangent or a point "
                "where the slope is undefined. Check the point carefully.")
    if mode == MODE_POLAR:
        return ("For F(r, theta) = 0, implicit differentiation gives\n"
                "F_r * dr/dtheta + F_theta = 0.\n\n"
                f"F_r = {sp.sstr(sp.diff(expression, r_symbol))}\n"
                f"F_theta = {sp.sstr(sp.diff(expression, theta_symbol))}\n\n"
                "Where F_r is not zero, dr/dtheta = -F_theta/F_r. "
                "If F_r is zero, inspect the point separately.")
    return ("For F(x, y) = 0, implicit differentiation gives\n"
            "dy/dx = -F_x/F_y when F_y is not zero.\n\n"
            f"F_x = {sp.sstr(sp.diff(expression, x_symbol))}\n"
            f"F_y = {sp.sstr(sp.diff(expression, y_symbol))}\n\n"
            "This slope is Cartesian. Converting to a polar tangent also "
            "requires care where the denominator vanishes.")


def _trapezoid(y, x):
    """NumPy 2.4 removed np.trapz; np.trapezoid is the new name."""
    return (np.trapezoid if hasattr(np, "trapezoid") else np.trapz)(y, x)


def _analysis_area(equation, mode, start, end, units, samples):
    if mode != MODE_EXPLICIT:
        return ("The simple polar area formula is intended for explicit "
                "r = f(theta) curves over a chosen interval.\n"
                "For implicit curves, area needs region and boundary analysis, "
                "which is not automatically determined by this estimate.")
    a0, a1 = angle_range_radians(start, end, units)
    angles = np.linspace(a0, a1, max(2000, int(samples)))
    radii = _as_array(equation.evaluate(theta=angles), angles.shape)
    valid = np.isfinite(radii)
    if np.count_nonzero(valid) < 2:
        return "Not enough valid values to estimate the area."
    if not np.all(valid):
        return ("The curve has undefined or non-finite values in this interval. "
                "Choose a smaller interval that avoids those points before "
                "estimating the area.")
    area = 0.5 * _trapezoid(radii ** 2, angles)
    return ("Polar area formula:\n"
            "A = 1/2 integral from alpha to beta of r(theta)^2 dtheta\n\n"
            f"Numerical estimate over [{a0:.5g}, {a1:.5g}] radians:\n"
            f"A ≈ {area:.8g} square units\n\n"
            "This integral measures area with tracing multiplicity. If the "
            "curve overlaps itself or traces a region more than once, the "
            "area of the distinct region may be different.")


def _analysis_symmetry(expression, mode):
    if mode == MODE_EXPLICIT:
        tests = [
            ("Polar-axis symmetry (theta -> -theta)",
             sp.simplify(expression.subs(theta_symbol, -theta_symbol))),
            ("Opposite-angle test (theta -> theta + pi)",
             sp.simplify(expression.subs(theta_symbol, theta_symbol + sp.pi))),
            ("Half-turn angle test (theta -> theta + 2*pi)",
             sp.simplify(expression.subs(theta_symbol, theta_symbol + 2 * sp.pi))),
        ]
        lines = [f"Equation: r = {sp.sstr(expression)}", "", "Substitution results:"]
        lines += [f"• {label}: {sp.sstr(result)}" for label, result in tests]
        lines += ["", "These substitutions help test symmetry and periodicity, "
                  "but a complete proof may need to account for negative radii "
                  "and equivalent polar representations."]
        return "\n".join(lines)
    if mode == MODE_POLAR:
        return "\n".join([
            f"Implicit equation: {sp.sstr(expression)} = 0", "",
            "Useful symmetry checks:",
            "• Polar axis: compare F(r, -theta) with F(r, theta).",
            "• Opposite direction: compare F(r, theta + pi).",
            "• Pole: test whether r = 0 can satisfy the equation.", "",
            "The program can display these substitutions, but deciding "
            "whether two expressions define exactly the same zero set "
            "sometimes needs extra algebraic reasoning."])
    swapped = {
        "X-axis": sp.simplify(expression.subs(y_symbol, -y_symbol)),
        "Y-axis": sp.simplify(expression.subs(x_symbol, -x_symbol)),
        "Origin": sp.simplify(expression.subs({x_symbol: -x_symbol,
                                               y_symbol: -y_symbol})),
    }
    return (f"Cartesian implicit equation: {sp.sstr(expression)} = 0\n\n"
            "To test symmetry, compare the equation after substitutions:\n"
            "• x-axis: y -> -y\n• y-axis: x -> -x\n• origin: (x, y) -> (-x, -y)\n\n"
            + "\n".join(f"{name} substitution: {sp.sstr(value)}"
                        for name, value in swapped.items())
            + "\n\nMatching expressions are a strong symmetry clue. For implicit "
            "equations, a nonzero constant multiple can also define the same curve.")


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def _load_preset():
    """Called when a family is chosen: fill in its example equation."""
    mode, equation, note = FAMILY_PRESETS[st.session_state.pol_family]
    st.session_state.pol_mode = mode
    st.session_state.pol_equation = equation
    st.session_state.pol_note = note


def _reset_example():
    _load_preset()
    st.session_state.update(pol_start=0.0, pol_end=360.0,
                            pol_units="Degrees", pol_grid=True)


def _convert_units():
    """Keep the same angles when switching degrees <-> radians."""
    to_radians = st.session_state.pol_units == "Radians"
    factor = math.pi / 180 if to_radians else 180 / math.pi
    for key in ("pol_start", "pol_end"):
        st.session_state[key] = round(st.session_state[key] * factor, 6)


def _remembered_slider(label, key, low, high, step):
    """A slider whose value survives while it is hidden (Beginner mode)."""
    value = st.slider(label, low, high, value=st.session_state[key], step=step,
                      key=key + "_widget")
    st.session_state[key] = value
    return value


def _analyze_clicked():
    """Runs when Analyze is pressed; reads the latest values from the widgets."""
    state = st.session_state
    try:
        state.pol_analysis_text = analyze(
            state.pol_analysis_choice, state.pol_equation, state.pol_mode,
            state.pol_start, state.pol_end, state.pol_units, state.pol_samples)
    except ValueError as error:
        state.pol_analysis_text = f"Analysis problem: {error}"


def render():
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)

    head, display = st.columns([4, 1])
    head.title("Project Polar Coordinates")
    head.caption("Polar Curve Explorer")
    display.radio("Display", ["Beginner", "Advanced"], key="pol_display",
                  horizontal=True)

    controls, graph = st.columns([1, 2])

    with controls:
        st.subheader("Curve")
        st.selectbox("Family", list(FAMILY_PRESETS), key="pol_family",
                     on_change=_load_preset)
        mode = st.selectbox("Equation type", MODES, key="pol_mode")
        text = st.text_input("Equation", key="pol_equation")
        if st.session_state.pol_display == "Advanced":
            st.caption("Use * for multiplication and ** for powers. "
                       "Examples: sin(theta), r**2, x**2 + y**2.")
        else:
            st.caption(equation_hint(mode))
        st.caption(st.session_state.pol_note)

        with st.container(border=True):
            st.markdown("**Angle range**  (used by explicit curves)")
            c1, c2 = st.columns(2)
            start = c1.number_input("From", step=1.0, format="%g", key="pol_start")
            end = c2.number_input("To", step=1.0, format="%g", key="pol_end")
            units = st.radio("Units", ["Degrees", "Radians"], horizontal=True,
                             key="pol_units", on_change=_convert_units)

        if st.session_state.pol_display == "Advanced":
            with st.container(border=True):
                st.markdown("**Advanced settings**")
                _remembered_slider("Implicit contour resolution", "pol_res", 80, 420, 10)
                st.caption("Higher resolution can reveal smaller details, "
                           "but takes longer.")
                _remembered_slider("Explicit sample points", "pol_samples", 300, 5000, 100)
                _remembered_slider("Implicit view half-width", "pol_limit", 2.0, 15.0, 0.5)

        st.checkbox("Show polar grid", key="pol_grid")
        st.button("Reset example", on_click=_reset_example)

    with graph:
        try:
            figure = make_figure(
                text, mode, start, end, units, st.session_state.pol_grid,
                st.session_state.pol_samples, st.session_state.pol_limit,
                st.session_state.pol_res)
        except ValueError as error:
            st.error(f"Could not plot this equation. {error}")
        else:
            st.pyplot(figure)

    with st.container(border=True):
        st.subheader("Analysis (optional)")
        a1, a2 = st.columns([3, 1])
        a1.selectbox("Show:", ANALYSES, key="pol_analysis_choice")
        a2.write("")
        a2.button("Analyze", on_click=_analyze_clicked)
        st.text(st.session_state.pol_analysis_text)
