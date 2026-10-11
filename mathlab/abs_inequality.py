"""Project Compound Absolute Value Inequalities.

Each inequality has the form   y (sign) a|x - h| + k
    a = steepness / direction,  h = left-right shift,  k = up-down shift
The two can be combined with AND (both true) or OR (at least one true).
"""

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from .formatting import SIGN_LATEX, abs_latex, fmt

SIGNS = [">", ">=", "<", "<="]
COLOR_1 = "#2878d0"
COLOR_2 = "#d97706"
COLOR_BOTH = (0.15, 0.55, 0.35, 0.35)


# ======================================================================
# MATH
# ======================================================================

def inequality_latex(a, h, k, sign):
    return f"y {SIGN_LATEX[sign]} {abs_latex(a, h, k)}"


def boundary(x, a, h, k):
    return a * np.abs(x - h) + k


def satisfies(y, boundary_y, sign):
    """Is  y (sign) boundary_y  true?  Works on single numbers or arrays."""
    if sign == ">":
        return y > boundary_y
    if sign == ">=":
        return y >= boundary_y
    if sign == "<":
        return y < boundary_y
    return y <= boundary_y


def get_graph_range(h1, k1, h2, k2):
    """Window centred on the two vertices with generous padding."""
    x_pad = max(5, abs(h1 - h2) * 2)
    y_pad = max(5, abs(k1 - k2) * 2)
    return (min(h1, h2) - x_pad, max(h1, h2) + x_pad,
            min(k1, k2) - y_pad, max(k1, k2) + y_pad)


def _style(sign):
    return "--" if sign in (">", "<") else "-"


def _finish(ax, x_min, x_max, y_min, y_max, title):
    ax.axhline(0, linewidth=1, color="black")
    ax.axvline(0, linewidth=1, color="black")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)


def single_figure(a, h, k, sign, window, title, color):
    """One inequality: V-shaped boundary and the shaded side."""
    x_min, x_max, y_min, y_max = window
    x = np.linspace(x_min, x_max, 500)
    edge = boundary(x, a, h, k)

    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.plot(x, edge, linestyle=_style(sign), linewidth=2, color=color,
            label=f"${inequality_latex(a, h, k, sign)}$")
    if sign in (">", ">="):
        ax.fill_between(x, edge, y_max, alpha=0.25, color=color)
    else:
        ax.fill_between(x, y_min, edge, alpha=0.25, color=color)
    ax.scatter([h], [k], s=60, zorder=5, color=color)
    ax.annotate(f"Vertex ({fmt(h)}, {fmt(k)})", (h, k), xytext=(8, 8),
                textcoords="offset points")
    _finish(ax, x_min, x_max, y_min, y_max, title)
    fig.tight_layout()
    return fig


def combined_figure(a1, h1, k1, sign1, a2, h2, k2, sign2, combine, window):
    """Test many points: AND needs both true, OR needs at least one."""
    x_min, x_max, y_min, y_max = window
    n = 400
    xs = np.linspace(x_min, x_max, n)
    ys = np.linspace(y_min, y_max, n)
    X, Y = np.meshgrid(xs, ys)

    first = satisfies(Y, boundary(X, a1, h1, k1), sign1)
    second = satisfies(Y, boundary(X, a2, h2, k2), sign2)
    if combine == "AND":
        solution = first & second
        explanation = "AND = points satisfying BOTH inequalities"
    else:
        solution = first | second
        explanation = "OR = points satisfying AT LEAST ONE inequality"

    image = np.zeros((n, n, 4))
    image[solution] = COLOR_BOTH

    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.imshow(image, extent=(x_min, x_max, y_min, y_max), origin="lower",
              aspect="auto", interpolation="nearest", zorder=0)
    x = np.linspace(x_min, x_max, 500)
    ax.plot(x, boundary(x, a1, h1, k1), linestyle=_style(sign1), linewidth=2,
            color=COLOR_1, label="Inequality 1")
    ax.plot(x, boundary(x, a2, h2, k2), linestyle=_style(sign2), linewidth=2,
            color=COLOR_2, label="Inequality 2")
    ax.scatter([h1], [k1], s=60, zorder=5, color=COLOR_1)
    ax.scatter([h2], [k2], s=60, zorder=5, color=COLOR_2)
    ax.text(0.02, 0.02, explanation, transform=ax.transAxes, fontsize=8,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
    _finish(ax, x_min, x_max, y_min, y_max, f"COMBINED SOLUTION — {combine}")
    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def _inputs(column, number, defaults, sign_default):
    """Inputs for one inequality inside ``column``."""
    a_def, h_def, k_def = defaults
    key = f"abs_{number}"
    with column:
        st.markdown(f"**Inequality {number}**:  y (sign) a|x − h| + k")
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a", value=a_def, step=1.0, format="%g", key=f"{key}_a")
        h = c2.number_input("h", value=h_def, step=1.0, format="%g", key=f"{key}_h")
        k = c3.number_input("k", value=k_def, step=1.0, format="%g", key=f"{key}_k")
        sign = st.selectbox("Sign", SIGNS, index=SIGNS.index(sign_default),
                            key=f"{key}_sign")
    return a, h, k, sign


def render():
    st.title("Project Compound Absolute Value Inequalities")
    st.write("Enter two absolute-value inequalities and combine them with "
             "**AND** or **OR**.")

    left, right = st.columns(2)
    a1, h1, k1, sign1 = _inputs(left, 1, (1.0, 0.0, 0.0), ">=")
    a2, h2, k2, sign2 = _inputs(right, 2, (1.0, 0.0, 2.0), "<=")

    combine = st.radio("Combine with", ["AND", "OR"], horizontal=True,
                       key="abs_combine")

    if a1 == 0 or a2 == 0:
        st.error("Please make sure both values of a are not 0.")
        return

    left.latex(inequality_latex(a1, h1, k1, sign1))
    right.latex(inequality_latex(a2, h2, k2, sign2))

    if combine == "AND":
        st.info("AND selected: the shaded region contains points that "
                "satisfy BOTH inequalities.")
    else:
        st.info("OR selected: the shaded region contains points that "
                "satisfy AT LEAST ONE inequality.")

    window = get_graph_range(h1, k1, h2, k2)
    g1, g2, g3 = st.columns(3)
    g1.pyplot(single_figure(a1, h1, k1, sign1, window, "INEQUALITY 1", COLOR_1))
    g2.pyplot(single_figure(a2, h2, k2, sign2, window, "INEQUALITY 2", COLOR_2))
    g3.pyplot(combined_figure(a1, h1, k1, sign1, a2, h2, k2, sign2,
                              combine, window))
