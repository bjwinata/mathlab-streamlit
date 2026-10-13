"""Project Completing the Square - y = ax^2 + bx + c  ->  y = a(x - h)^2 + k."""

import streamlit as st

from .formatting import (EPS, fmt, lead_coeff, poly_latex, signed_const,
                         squared_binomial, vertex_form_latex)


# ======================================================================
# MATH
# ======================================================================

def _paren(value):
    """Wrap negative numbers in brackets: -2 -> (-2)."""
    return f"({fmt(value)})" if value < 0 else fmt(value)


def _group(a, inner):
    """a( inner ) with the coefficient tidied up (1 -> nothing, -1 -> '-')."""
    return f"{lead_coeff(a)}\\left({inner}\\right)"


def solve_steps(a, b, c):
    """Return (steps, h, k).  ``steps`` is a list of dicts with keys
    number, title, text, latex, note.  ``a`` must not be zero."""
    h = -b / (2 * a)
    k = c - b ** 2 / (4 * a)

    ratio = b / a            # coefficient of x after factoring out a
    half = ratio / 2
    half_sq = half ** 2
    leftover = c - a * half_sq

    steps = []

    # Step 1 - factor a from the x^2 and x terms
    if abs(a - 1) < EPS:
        text = "Because a = 1, there is nothing to factor from the x² and x terms."
        latex = "y = " + poly_latex(1, b, c)
    else:
        text = f"Factor {fmt(a)} from the x² and x terms."
        latex = "y = " + _group(a, poly_latex(1, ratio, 0)) + signed_const(c)
    steps.append(dict(title="Factor the x² and x terms", text=text,
                      latex=latex, note=None))

    # Step 2 - half of the x coefficient
    note = None
    if abs(ratio) < EPS:
        note = ("The x coefficient is 0, so this quadratic is already "
                "in vertex form (h = 0).")
    steps.append(dict(
        title="Take half of the x coefficient",
        text="Look at the coefficient of x inside the parentheses. "
             "Divide it by 2.",
        latex=f"\\tfrac{{1}}{{2}}\\left({fmt(ratio)}\\right) = {fmt(half)}",
        note=note))

    # Step 3 - square it
    steps.append(dict(
        title="Square the result",
        text="Now square the number you obtained. This is the number needed "
             "to create a perfect-square trinomial.",
        latex=f"\\left({fmt(half)}\\right)^{{2}} = {fmt(half_sq)}",
        note=None))

    # Step 4 - add and subtract it
    inner = poly_latex(1, ratio, 0) + f" + {fmt(half_sq)} - {fmt(half_sq)}"
    steps.append(dict(
        title="Add and subtract the same number",
        text="Add the number inside the parentheses, but immediately "
             "subtract the same number. This keeps the equation balanced.",
        latex="y = " + _group(a, inner) + signed_const(c),
        note=None))

    # Step 5 - perfect square
    steps.append(dict(
        title="Create the perfect square",
        text="The first three terms form a perfect-square trinomial. "
             "Rewrite them as a squared binomial.",
        latex=f"y = {lead_coeff(a)}{squared_binomial(-half)}{signed_const(leftover)}",
        note=(f"The constant is c − a·(½·b/a)² = {fmt(c)} − "
              f"{_paren(a)}·{fmt(half_sq)} = {fmt(leftover)}.")))

    # Step 6 - final answer
    steps.append(dict(
        title="Final Answer",
        text="The quadratic is now in vertex form. The vertex can be read "
             "directly from y = a(x − h)² + k.",
        latex=vertex_form_latex(a, h, k), note=None))

    for number, step in enumerate(steps, start=1):
        step["number"] = number
    return steps, h, k


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def render():
    st.title("Project Completing the Square")
    st.write("Convert a quadratic from standard form to vertex form — "
             "step by step.")

    with st.container(border=True):
        st.markdown("**Enter your quadratic:** y = ax² + bx + c")
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a", value=1.0, step=1.0, format="%g", key="cts_a")
        b = c2.number_input("b", value=6.0, step=1.0, format="%g", key="cts_b")
        c = c3.number_input("c", value=5.0, step=1.0, format="%g", key="cts_c")
        st.latex("y = " + poly_latex(a, b, c))

    if a == 0:
        st.error("a cannot be 0. Please enter a quadratic equation.")
        return

    steps, h, k = solve_steps(a, b, c)

    with st.container(border=True):
        left, right = st.columns([2, 1])
        left.markdown("**Vertex form**")
        left.latex(vertex_form_latex(a, h, k))
        right.markdown("**Vertex**")
        right.latex(f"({fmt(h)},\\ {fmt(k)})")

    st.subheader("How We Got There")
    for step in steps:
        with st.container(border=True):
            st.markdown(f"**Step {step['number']} — {step['title']}**")
            st.write(step["text"])
            st.latex(step["latex"])
            if step["note"]:
                st.caption(step["note"])
