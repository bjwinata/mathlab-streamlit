"""Project Linear Inequality - graph two inequalities y (sign) mx + b."""

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from .formatting import SIGN_LATEX, linear_latex

SIGNS = [">", ">=", "<", "<="]
LINE_1_COLOR = "blue"
LINE_2_COLOR = "green"


# ======================================================================
# MATH
# ======================================================================

def inequality_latex(sign, m, b):
    return f"y {SIGN_LATEX[sign]} {linear_latex(m, b)}"


def find_intersection(m1, b1, m2, b2):
    """Where y = m1 x + b1 meets y = m2 x + b2 (None when parallel)."""
    if m1 == m2:
        return None
    x = (b2 - b1) / (m1 - m2)
    return x, m1 * x + b1


def holds(y, line_y, sign):
    """Does the point (x, y) satisfy  y (sign) line_y ?  Works on arrays."""
    if sign == ">":
        return y > line_y
    if sign == ">=":
        return y >= line_y
    if sign == "<":
        return y < line_y
    return y <= line_y


def choose_graph_size(intersection):
    """Centre the window on the intersection (or use -10..10)."""
    if intersection is None:
        return -10, 10, -10, 10
    x, y = intersection
    x_range = abs(x) + 5 if abs(x) > 5 else 10
    y_range = abs(y) + 5 if abs(y) > 5 else 10
    return x - x_range, x + x_range, y - y_range, y + y_range


def make_figure(sign1, m1, b1, sign2, m2, b2):
    intersection = find_intersection(m1, b1, m2, b2)
    x_min, x_max, y_min, y_max = choose_graph_size(intersection)

    # Test the centre of many small cells: which inequalities are true there?
    cols, rows = 500, 350
    xs = x_min + (np.arange(cols) + 0.5) * (x_max - x_min) / cols
    ys = y_min + (np.arange(rows) + 0.5) * (y_max - y_min) / rows
    X, Y = np.meshgrid(xs, ys)
    first = holds(Y, m1 * X + b1, sign1)
    second = holds(Y, m2 * X + b2, sign2)

    image = np.zeros((rows, cols, 4))
    image[first] = (0.15, 0.35, 1.00, 0.12)           # blue tint
    image[second] = (0.10, 0.65, 0.20, 0.12)          # green tint
    image[first & second] = (1.00, 0.00, 0.00, 0.35)  # red = both

    fig = Figure(figsize=(8, 5.5))
    ax = fig.add_subplot(111)
    ax.imshow(image, extent=(x_min, x_max, y_min, y_max), origin="lower",
              aspect="auto", interpolation="nearest", zorder=0)

    line_x = np.array([x_min, x_max])
    for sign, m, b, color in ((sign1, m1, b1, LINE_1_COLOR),
                              (sign2, m2, b2, LINE_2_COLOR)):
        # strict inequality -> dashed boundary, inclusive -> solid
        style = "--" if sign in (">", "<") else "-"
        ax.plot(line_x, m * line_x + b, color=color, linewidth=2.5,
                linestyle=style, zorder=3,
                label=f"${inequality_latex(sign, m, b)}$")

    ax.axhline(0, color="black", linewidth=1.5, zorder=2)
    ax.axvline(0, color="black", linewidth=1.5, zorder=2)

    if intersection is not None:
        ix, iy = intersection
        ax.plot([ix], [iy], "o", color="black", markersize=7, zorder=5)
        ax.annotate(f"({ix:.2f}, {iy:.2f})", (ix, iy), xytext=(8, 10),
                    textcoords="offset points", fontweight="bold")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, color="#dddddd", zorder=1)
    ax.set_axisbelow(True)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper left")
    fig.tight_layout()
    return fig, intersection


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def render():
    st.title("Project Linear Inequality")
    st.write("Graph two linear inequalities and find where **both** are true.")

    head = st.columns([1, 1, 1, 1])
    for col, text in zip(head, ["Inequality", "Sign", "Slope (m)", "Intercept (b)"]):
        col.markdown(f"**{text}**")

    row1 = st.columns([1, 1, 1, 1])
    row1[0].write("Inequality 1")
    sign1 = row1[1].selectbox("Sign 1", SIGNS, index=0, key="li_sign1",
                              label_visibility="collapsed")
    m1 = row1[2].number_input("Slope 1", value=2.0, step=1.0, format="%g",
                              key="li_m1", label_visibility="collapsed")
    b1 = row1[3].number_input("Intercept 1", value=1.0, step=1.0, format="%g",
                              key="li_b1", label_visibility="collapsed")

    row2 = st.columns([1, 1, 1, 1])
    row2[0].write("Inequality 2")
    sign2 = row2[1].selectbox("Sign 2", SIGNS, index=2, key="li_sign2",
                              label_visibility="collapsed")
    m2 = row2[2].number_input("Slope 2", value=-1.0, step=1.0, format="%g",
                              key="li_m2", label_visibility="collapsed")
    b2 = row2[3].number_input("Intercept 2", value=7.0, step=1.0, format="%g",
                              key="li_b2", label_visibility="collapsed")

    st.latex(f"{inequality_latex(sign1, m1, b1)} \\quad \\textbf{{AND}} \\quad "
             f"{inequality_latex(sign2, m2, b2)}")

    fig, intersection = make_figure(sign1, m1, b1, sign2, m2, b2)
    st.pyplot(fig)

    if intersection is not None:
        x, y = intersection
        st.info(f"**Intersection:** ({x:.2f}, {y:.2f})")
    else:
        st.info("The two boundary lines are parallel, so they do not have "
                "an intersection.")
    st.caption("Blue tint = inequality 1 is true · Green tint = inequality 2 "
               "is true · **Red = BOTH are true** · Dashed line = the boundary "
               "is not included (< or >) · Solid line = included (≤ or ≥).")
