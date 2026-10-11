"""Project Compound Inequality Number Line.

The student enters two inequalities of the form  x (sign) number,
chooses AND / OR, and sees three aligned number lines:
inequality 1, inequality 2, and the combined solution.
"""

import math

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from .formatting import SIGN_LATEX, fmt

SIGNS = ["<", "<=", ">", ">="]
BLUE = "#2878d0"
GREEN = "#15966a"
RED = "#d62728"


# ======================================================================
# MATH
# ======================================================================

def is_true(x, sign, number):
    """Does x satisfy  x (sign) number ?  Works on numbers or arrays."""
    if sign == "<":
        return x < number
    if sign == "<=":
        return x <= number
    if sign == ">":
        return x > number
    return x >= number


def combined_solution(x, sign1, n1, sign2, n2, combine):
    first = is_true(x, sign1, n1)
    second = is_true(x, sign2, n2)
    return (first & second) if combine == "AND" else (first | second)


def axis_limits(n1, n2):
    """Whole-number window that comfortably contains both endpoints."""
    lo = math.floor(min(n1, n2)) - 3
    hi = math.ceil(max(n1, n2)) + 3
    if hi - lo < 8:
        centre = (n1 + n2) / 2
        lo, hi = math.floor(centre) - 4, math.floor(centre) + 4
    return lo, hi


def true_runs(x, mask):
    """Contiguous stretches (start, end) where mask is True."""
    runs, start = [], None
    for i, flag in enumerate(mask):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            runs.append((x[start], x[i - 1]))
            start = None
    if start is not None:
        runs.append((x[start], x[-1]))
    return runs


def _prepare_axis(ax, lo, hi, title):
    ax.set_xlim(lo - 0.6, hi + 0.9)
    ax.set_ylim(-1, 1)
    ax.set_xticks(range(lo, hi + 1))
    ax.tick_params(axis="x", length=6, width=2, labelsize=10, labelbottom=True)
    ax.get_yaxis().set_visible(False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["bottom"].set_linewidth(2.5)
    ax.set_title(title, fontweight="bold", loc="center", pad=14)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)


def _endpoint(ax, number, sign):
    """Open circle for < and >, closed circle for <= and >=."""
    closed = sign in ("<=", ">=")
    ax.plot([number], [0], "o", markersize=13, zorder=6,
            markerfacecolor=RED if closed else "white",
            markeredgecolor=RED, markeredgewidth=2.5)


def make_figure(sign1, n1, sign2, n2, combine):
    lo, hi = axis_limits(n1, n2)
    left_end, right_end = lo - 0.6, hi + 0.9

    fig = Figure(figsize=(9, 6.2))
    axes = fig.subplots(3, 1, sharex=True)

    # Lines 1 and 2: a single ray each
    for ax, label, sign, number in ((axes[0], "Inequality 1", sign1, n1),
                                    (axes[1], "Inequality 2", sign2, n2)):
        _prepare_axis(ax, lo, hi, f"{label}:  x {sign} {fmt(number)}")
        if sign in ("<", "<="):
            ax.hlines(0, left_end, number, color=BLUE, linewidth=9, zorder=4)
        else:
            ax.hlines(0, number, right_end, color=BLUE, linewidth=9, zorder=4)
        _endpoint(ax, number, sign)

    # Line 3: test many points and colour the ones that satisfy AND / OR
    ax = axes[2]
    _prepare_axis(ax, lo, hi, f"Combined Solution: {combine}")
    x = np.linspace(left_end, right_end, 4000)
    for start, end in true_runs(x, combined_solution(x, sign1, n1, sign2, n2, combine)):
        ax.hlines(0, start, end, color=GREEN, linewidth=9, zorder=4)
    _endpoint(ax, n1, sign1)
    _endpoint(ax, n2, sign2)

    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def render():
    st.title("Compound Inequality Number Line")
    st.write("Enter two inequalities, then choose **AND** or **OR** to see "
             "the combined solution.")

    with st.expander("How to read the number lines"):
        st.markdown(
            "- **Open circle** — `<` or `>` (the number itself is *not* included)\n"
            "- **Closed circle** — `<=` or `>=` (the number *is* included)\n"
            "- **AND** — both inequalities must be true\n"
            "- **OR** — at least one inequality must be true")

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.4])
    c1.markdown("**Inequality 1**  x")
    sign1 = c2.selectbox("Sign 1", SIGNS, index=2, key="nl_sign1",
                         label_visibility="collapsed")
    n1 = c3.number_input("Number 1", value=2.0, step=1.0, format="%g",
                         key="nl_n1", label_visibility="collapsed")
    combine = c5.radio("Combine with", ["AND", "OR"], horizontal=True,
                       key="nl_combine")

    d1, d2, d3, d4, d5 = st.columns([1, 1, 1, 1, 1.4])
    d1.markdown("**Inequality 2**  x")
    sign2 = d2.selectbox("Sign 2", SIGNS, index=0, key="nl_sign2",
                         label_visibility="collapsed")
    n2 = d3.number_input("Number 2", value=6.0, step=1.0, format="%g",
                         key="nl_n2", label_visibility="collapsed")

    st.latex(f"x {SIGN_LATEX[sign1]} {fmt(n1)} \\quad \\textbf{{{combine}}} \\quad "
             f"x {SIGN_LATEX[sign2]} {fmt(n2)}")

    st.pyplot(make_figure(sign1, n1, sign2, n2, combine))

    st.info(f"Using **{combine}**: look at the **green** part of the third "
            "number line.")
