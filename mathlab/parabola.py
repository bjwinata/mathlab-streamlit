"""Project Parabola - analyse y = ax^2 + bx + c and graph it."""

import math
from dataclasses import dataclass, field

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from .formatting import (EPS, factor_latex, fmt, lead_coeff, md_table,
                         point, poly_latex, vertex_form_latex)


# ======================================================================
# MATH (no Streamlit code below this line until render())
# ======================================================================

@dataclass
class Parabola:
    a: float
    b: float
    c: float
    discriminant: float = 0.0
    vertex_x: float = 0.0
    vertex_y: float = 0.0
    roots: list = field(default_factory=list)        # real roots, ascending
    kind: str = ""                                    # 'two', 'one', 'complex'


def analyze(a, b, c):
    """Compute the basic quantities. ``a`` must not be zero."""
    disc = b ** 2 - 4 * a * c
    vx = -b / (2 * a)
    vy = a * vx ** 2 + b * vx + c

    if abs(disc) < EPS:
        kind, roots = "one", [vx]
    elif disc > 0:
        kind = "two"
        roots = sorted([(-b + math.sqrt(disc)) / (2 * a),
                        (-b - math.sqrt(disc)) / (2 * a)])
    else:
        kind, roots = "complex", []
    return Parabola(a, b, c, disc, vx, vy, roots, kind)


def forms(p):
    """Standard, vertex and factored forms as LaTeX (factored may be None)."""
    standard = "y = " + poly_latex(p.a, p.b, p.c)
    vertex = vertex_form_latex(p.a, p.vertex_x, p.vertex_y)
    lead = lead_coeff(p.a)
    if p.kind == "two":
        factored = f"y = {lead}{factor_latex(p.roots[0])}{factor_latex(p.roots[1])}"
    elif p.kind == "one":
        r = p.roots[0]
        square = "x^{2}" if abs(r) < EPS else f"{factor_latex(r)}^{{2}}"
        factored = f"y = {lead}{square}"
    else:
        factored = None
    return standard, vertex, factored


def properties(p):
    """List of (name, value) rows for the properties table."""
    a, b, c = p.a, p.b, p.c
    vx, vy = p.vertex_x, p.vertex_y
    focal = 1 / (4 * a)

    if p.kind == "two":
        classification = "Two real roots"
        roots = f"x₁ = {fmt(p.roots[0], 6)}, x₂ = {fmt(p.roots[1], 6)}"
        x_int = f"({fmt(p.roots[0], 6)}, 0), ({fmt(p.roots[1], 6)}, 0)"
    elif p.kind == "one":
        classification = "One repeated real root"
        roots = f"x = {fmt(p.roots[0], 6)}"
        x_int = f"({fmt(p.roots[0], 6)}, 0)"
    else:
        classification = "Two complex roots"
        re_part = -b / (2 * a)
        im_part = math.sqrt(-p.discriminant) / abs(2 * a)
        roots = (f"x₁ = {fmt(re_part, 6)} + {fmt(im_part, 6)}i, "
                 f"x₂ = {fmt(re_part, 6)} - {fmt(im_part, 6)}i")
        x_int = "None"

    if a > 0:
        direction, extreme = "Opens upward", f"Minimum = {fmt(vy, 6)}"
        value_range = f"y ≥ {fmt(vy, 6)}"
        increasing, decreasing = f"x > {fmt(vx, 6)}", f"x < {fmt(vx, 6)}"
    else:
        direction, extreme = "Opens downward", f"Maximum = {fmt(vy, 6)}"
        value_range = f"y ≤ {fmt(vy, 6)}"
        increasing, decreasing = f"x < {fmt(vx, 6)}", f"x > {fmt(vx, 6)}"

    return [
        ("Classification", classification),
        ("Discriminant", fmt(p.discriminant, 6)),
        ("Roots", roots),
        ("X-intercepts", x_int),
        ("Vertex", point(vx, vy, 6)),
        ("Axis of symmetry", f"x = {fmt(vx, 6)}"),
        ("Direction", direction),
        ("Y-intercept", f"(0, {fmt(c, 6)})"),
        ("Minimum / Maximum", extreme),
        ("Domain", "All real numbers"),
        ("Range", value_range),
        ("Increasing", increasing),
        ("Decreasing", decreasing),
        ("Focus", point(vx, vy + focal, 6)),
        ("Directrix", f"y = {fmt(vy - focal, 6)}"),
        ("Latus rectum", f"Length = {fmt(abs(4 * focal), 6)}"),
    ]


def graph_range(p):
    """Zoom so the vertex, intercepts and origin are visible with padding."""
    xs = [p.vertex_x, 0, 0] + list(p.roots)
    ys = [p.vertex_y, p.c, 0] + [0] * len(p.roots)

    width = (max(xs) - min(xs)) or 10
    height = (max(ys) - min(ys)) or 10
    x_pad = max(width * 0.25, 3)
    y_pad = max(height * 0.25, 3)

    x_min, x_max = min(xs) - x_pad, max(xs) + x_pad
    y_min, y_max = min(ys) - y_pad, max(ys) + y_pad

    if x_max - x_min < 10:
        mid = (x_min + x_max) / 2
        x_min, x_max = mid - 5, mid + 5
    if y_max - y_min < 10:
        mid = (y_min + y_max) / 2
        y_min, y_max = mid - 5, mid + 5
    return x_min, x_max, y_min, y_max


def fit_to_frame(x_min, x_max, y_min, y_max, ratio=1.15):
    """The graph uses equal x/y scale, so widen the shorter side until the
    window has the same shape as the plot area (otherwise it looks squeezed)."""
    width, height = x_max - x_min, y_max - y_min
    if width / height < ratio:
        extra = (height * ratio - width) / 2
        x_min, x_max = x_min - extra, x_max + extra
    else:
        extra = (width / ratio - height) / 2
        y_min, y_max = y_min - extra, y_max + extra
    return x_min, x_max, y_min, y_max


def make_figure(p):
    x_min, x_max, y_min, y_max = fit_to_frame(*graph_range(p))
    x = np.linspace(x_min, x_max, 600)
    y = p.a * x ** 2 + p.b * x + p.c

    fig = Figure(figsize=(7, 6.2))
    ax = fig.add_subplot(111)
    ax.plot(x, y, linewidth=2, label="Parabola")
    ax.scatter([p.vertex_x], [p.vertex_y], s=70, zorder=5, label="Vertex")
    ax.scatter([0], [p.c], s=60, zorder=5, label="Y-intercept")
    if p.roots:
        ax.scatter(p.roots, [0] * len(p.roots), s=60, zorder=5,
                   label="X-intercept")
    ax.axhline(0, linewidth=1, color="black")
    ax.axvline(0, linewidth=1, color="black")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"${'y = ' + poly_latex(p.a, p.b, p.c)}$")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend(fontsize=9, framealpha=0.9)
    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def render():
    st.title("Project Parabola")
    st.write("Enter the coefficients of **y = ax² + bx + c**. "
             "Everything below updates as you type.")

    c1, c2, c3 = st.columns(3)
    a = c1.number_input("a", value=1.0, step=1.0, format="%g", key="par_a")
    b = c2.number_input("b", value=0.0, step=1.0, format="%g", key="par_b")
    c = c3.number_input("c", value=0.0, step=1.0, format="%g", key="par_c")

    if a == 0:
        st.warning("**Not a parabola:** a = 0. Choose a non-zero value for a.")
        return

    p = analyze(a, b, c)
    standard, vertex, factored = forms(p)

    left, right = st.columns([1, 1.15])

    with left:
        st.subheader("Equation forms")
        st.caption("Standard form")
        st.latex(standard)
        st.caption("Vertex form")
        st.latex(vertex)
        st.caption("Factored form")
        if factored:
            st.latex(factored)
        else:
            st.write("No real factored form (the roots are complex).")

        st.subheader("Calculated properties")
        st.markdown(md_table(["Property", "Value"], properties(p)))

    with right:
        st.subheader("Live graph")
        st.pyplot(make_figure(p))
