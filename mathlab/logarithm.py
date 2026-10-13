"""Project Logarithm - explore f(x) = a * log_b(x - h) + k.

Five tabs: Overview, Transformations, Inverse & Reflection,
Base Explorer, Practice / Challenge.

    base b > 0 and b != 1,   x - h > 0
    inverse:  f^-1(x) = h + b ** ((x - k) / a)      (needs a != 0)
"""

import math
import random

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

from .formatting import EPS, fmt, lead_coeff, md_table, signed_const, x_minus

# Colours are shared by every tab so each function is easy to recognise.
BLACK = "#222222"    # original logarithm
BLUE = "#2878d0"     # changed logarithm
GREEN = "#15966a"    # exponential
PURPLE = "#8b5cf6"   # inverse of the changed logarithm
ORANGE = "#d97706"   # vertical asymptote
GRAY = "#888888"     # reflection line y = x

DEFAULT_SETTINGS = {"log_base": 2.0, "log_a": 1.0, "log_h": 0.0, "log_k": 0.0}
CURVE_SWITCHES = [   # (state key, label, default)
    ("log_show_original", "Original logarithm (black)", True),
    ("log_show_changed", "Changed logarithm (blue)", True),
    ("log_show_exponential", "Exponential (green)", True),
    ("log_show_inverse", "Inverse of changed log (purple)", False),
    ("log_show_yx", "Reflection line y = x", False),
    ("log_show_asymptote", "Vertical asymptote", True),
    ("log_show_points", "Key points", True),
]
QUESTIONS = [
    "Identify the horizontal shift",
    "Identify the vertical shift",
    "Find the vertical asymptote",
    "Find the inverse function",
    "Determine the domain",
]
HINTS = {
    QUESTIONS[0]: "Look inside the logarithm. The graph's vertical asymptote is x = h.",
    QUESTIONS[1]: "Look at the number added after the logarithm is multiplied by a.",
    QUESTIONS[2]: "The logarithm's input becomes zero at the vertical asymptote.",
    QUESTIONS[3]: "Swap x and y, then solve for y. The logarithm becomes an exponential.",
    QUESTIONS[4]: "The expression inside the logarithm must be greater than zero.",
}


# ======================================================================
# MATH
# ======================================================================

def is_valid_base(base):
    return base > 0 and not math.isclose(base, 1.0)


def original_log_values(x, base):
    """log_base(x); NaN where x <= 0 so the graph shows a gap."""
    y = np.full_like(x, np.nan, dtype=float)
    if not is_valid_base(base):
        return y
    ok = x > 0
    y[ok] = np.log(x[ok]) / math.log(base)
    return y


def changed_log_values(x, a, h, k, base):
    """a * log_base(x - h) + k; NaN where x <= h (or a = 0)."""
    y = np.full_like(x, np.nan, dtype=float)
    if not is_valid_base(base) or math.isclose(a, 0.0):
        return y
    ok = x > h
    y[ok] = a * np.log(x[ok] - h) / math.log(base) + k
    return y


def changed_log_inverse_values(x, a, h, k, base):
    """h + base ** ((x - k) / a); NaN when no inverse exists."""
    y = np.full_like(x, np.nan, dtype=float)
    if not is_valid_base(base) or math.isclose(a, 0.0):
        return y
    exponent = np.clip((x - k) / a, -100, 100)    # avoid overflow
    y = h + np.power(base, exponent)
    y[~np.isfinite(y)] = np.nan
    return y


def log_latex(base, a, h, k):
    """f(x) = a log_b(x - h) + k"""
    return (f"f(x) = {lead_coeff(a)}\\log_{{{fmt(base)}}}"
            f"\\left({x_minus(h)}\\right){signed_const(k)}")


def inverse_latex(base, a, h, k):
    numerator = "x" if abs(k) < EPS else (
        f"x - {fmt(k)}" if k > 0 else f"x + {fmt(-k)}")
    exponent = numerator if abs(a - 1) < EPS else f"\\frac{{{numerator}}}{{{fmt(a)}}}"
    shift = "" if abs(h) < EPS else f"{fmt(h)} + "
    return f"f^{{-1}}(x) = {shift}{fmt(base)}^{{{exponent}}}"


def inverse_text(base, a, h, k):
    return f"f⁻¹(x) = {h:g} + {base:g}^((x − ({k:g})) / {a:g})"


def function_text(base, a, h, k):
    return f"f(x) = {a:g} × log base {base:g}(x − ({h:g})) + ({k:g})"


def practice_solution(question, base, a, h, k):
    if question == QUESTIONS[0]:
        return (f"The horizontal shift parameter is h = {h:g}.\n\n"
                f"The vertical asymptote is x = {h:g}.")
    if question == QUESTIONS[1]:
        return (f"The vertical shift parameter is k = {k:g}.\n\n"
                "A positive k moves the curve up; a negative k moves it down.")
    if question == QUESTIONS[2]:
        return f"The vertical asymptote is x = {h:g}."
    if question == QUESTIONS[3]:
        if math.isclose(a, 0.0):
            return ("There is no inverse function when a = 0, because the "
                    "formula becomes a constant instead of a one-to-one curve.")
        return ("Swap x and y and solve for y.\n\n"
                f"Answer: {inverse_text(base, a, h, k)}")
    return (f"The logarithm needs x − h > 0.\n\n"
            f"So x > {h:g}. The domain is all x-values greater than {h:g}.")


# ======================================================================
# GRAPHS
# ======================================================================

def _new_axes(size=(7.5, 5.2)):
    fig = Figure(figsize=size)
    ax = fig.add_subplot(111)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig, ax


def _finish(ax, title, xlim=(-8, 12), ylim=(-8, 12), legend=True):
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.axvline(0, color="#555555", linewidth=0.8)
    ax.grid(True, alpha=0.22)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(title)
    if legend:
        ax.legend(loc="best", fontsize=8)


def overview_figure(base):
    fig, ax = _new_axes()
    pos_x = np.linspace(0.02, 12, 700)
    exp_x = np.linspace(-5, 5, 700)
    ax.plot(pos_x, original_log_values(pos_x, base), color=BLACK,
            linewidth=2.3, label=f"log base {base:g}(x)")
    ax.plot(exp_x, np.power(base, exp_x), color=GREEN, linewidth=2.3,
            label=f"{base:g} to the power x")
    ax.scatter([1, base], [0, 1], color=BLACK, zorder=5)
    ax.scatter([0, 1], [1, base], color=GREEN, zorder=5)
    ax.annotate("(1, 0)", (1, 0), xytext=(7, -16), textcoords="offset points")
    ax.annotate(f"({base:g}, 1)", (base, 1), xytext=(7, 7),
                textcoords="offset points")
    _finish(ax, "The logarithm and its exponential inverse", (-5, 12), (-5, 12))
    fig.tight_layout()
    return fig


def transformations_figure(base, a, h, k, show):
    fig, ax = _new_axes()
    x = np.linspace(-8, 12, 900)
    nonzero = not math.isclose(a, 0.0)

    if show["log_show_original"]:
        ox = np.linspace(0.02, 15, 700)
        ax.plot(ox, original_log_values(ox, base), color=BLACK, linewidth=2.2,
                label="Original logarithm")
    if show["log_show_changed"] and nonzero:
        ax.plot(x, changed_log_values(x, a, h, k, base), color=BLUE,
                linewidth=2.4, label="Changed logarithm")
    if show["log_show_exponential"]:
        ex = np.linspace(-5, 5, 700)
        ax.plot(ex, np.power(base, ex), color=GREEN, linewidth=1.8,
                label="Exponential inverse")
    if show["log_show_inverse"] and nonzero:
        ix = np.linspace(-8, 8, 700)
        ax.plot(ix, changed_log_inverse_values(ix, a, h, k, base),
                color=PURPLE, linewidth=2.0, label="Inverse of changed log")
    if show["log_show_yx"]:
        ax.plot(x, x, "--", color=GRAY, linewidth=1.3, label="y = x")
    if show["log_show_asymptote"] and show["log_show_changed"] and nonzero:
        ax.axvline(h, color=ORANGE, linestyle=":", linewidth=1.8,
                   label=f"Vertical asymptote x = {h:g}")
    if show["log_show_points"] and nonzero:
        px, py = [h + 1, h + base], [k, k + a]
        ax.scatter(px, py, color=BLUE, zorder=5)
        ax.annotate(f"({px[0]:g}, {py[0]:g})", (px[0], py[0]), xytext=(5, 6),
                    textcoords="offset points", fontsize=8)
        ax.annotate(f"({px[1]:g}, {py[1]:g})", (px[1], py[1]), xytext=(5, 6),
                    textcoords="offset points", fontsize=8)

    _finish(ax, "Logarithmic transformations",
            legend=bool(ax.get_legend_handles_labels()[0]))
    fig.tight_layout()
    return fig


def inverse_figure(base, a, h, k, show):
    """Original/changed curves and their inverses, mirrored across y = x.
    A curve whose checkbox is off is faded, so 'Emphasize' has a clear effect."""
    fig, ax = _new_axes()
    log_x = np.linspace(0.02, 12, 700)
    exp_x = np.linspace(-5, 5, 700)
    x = np.linspace(-8, 12, 900)

    def weight(key):
        return 1.0 if show[key] else 0.22

    ax.plot(log_x, original_log_values(log_x, base), color=BLACK, linewidth=2,
            alpha=weight("log_show_original"), label="Original logarithm")
    ax.plot(exp_x, np.power(base, exp_x), color=GREEN, linewidth=2,
            alpha=weight("log_show_exponential"), label="Exponential inverse")
    if not math.isclose(a, 0.0):
        ax.plot(x, changed_log_values(x, a, h, k, base), color=BLUE,
                linewidth=2, alpha=weight("log_show_changed"),
                label="Changed logarithm")
        ax.plot(x, changed_log_inverse_values(x, a, h, k, base), color=PURPLE,
                linewidth=2.6 if show["log_show_inverse"] else 2,
                alpha=1.0 if show["log_show_inverse"] else 0.6,
                label="Inverse of changed logarithm")
    ax.plot(x, x, "--", color=GRAY if show["log_show_yx"] else "#cccccc",
            linewidth=1.4, label="y = x")
    _finish(ax, "Functions and their inverses")
    fig.tight_layout()
    return fig


def base_comparison_figure():
    fig, ax = _new_axes()
    x = np.linspace(0.02, 12, 700)
    ax.plot(x, original_log_values(x, 2), color=BLUE, linewidth=2.2, label="log₂(x)")
    ax.plot(x, original_log_values(x, 10), color=ORANGE, linewidth=2.2, label="log₁₀(x)")
    ax.plot(x, original_log_values(x, math.e), color=GREEN, linewidth=2.2, label="ln(x)")
    _finish(ax, "Changing the base changes the shape", (-0.5, 12), (-4, 4))
    fig.tight_layout()
    return fig


def practice_figure(base, a, h, k):
    fig, ax = _new_axes((7, 4.5))
    x = np.linspace(-8, 12, 900)
    ax.plot(x, changed_log_values(x, a, h, k, base), color=BLUE, linewidth=2.4,
            label="Practice function")
    ax.axvline(h, color=ORANGE, linestyle=":", linewidth=1.6,
               label=f"Vertical asymptote x = {h:g}")
    _finish(ax, "Current practice graph")
    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def _reset_settings():
    st.session_state.update(DEFAULT_SETTINGS)


def _random_settings():
    st.session_state.log_base = random.choice([2.0, 3.0, 4.0, 5.0])
    st.session_state.log_a = random.choice([-2.0, -1.0, 1.0, 2.0])
    st.session_state.log_h = random.choice([-3.0, -2.0, 1.0, 2.0, 3.0])
    st.session_state.log_k = random.choice([-3.0, -1.0, 1.0, 2.0, 3.0])


def _emphasize_inverse():
    """Show only the transformed inverse (plus y = x), as in the original app."""
    st.session_state.update({
        "log_show_changed": False, "log_show_inverse": True,
        "log_show_original": False, "log_show_exponential": False,
        "log_show_yx": True,
    })


def _tab_overview(base):
    left, right = st.columns([1, 2])
    with left:
        st.subheader("The two original functions")
        st.latex(f"y = \\log_{{{fmt(base)}}}(x)")
        st.latex(f"y = {fmt(base)}^{{x}}")
        st.markdown(
            f"**Logarithm** y = log base {base:g}(x)\n\n"
            "- Domain: x > 0\n- Range: all real numbers\n"
            "- Vertical asymptote: x = 0\n"
            f"- Key points: (1, 0) and ({base:g}, 1)\n\n"
            f"**Exponential** y = {base:g}^x\n\n"
            "- Domain: all real numbers\n- Range: y > 0\n"
            "- Horizontal asymptote: y = 0\n"
            f"- Key points: (0, 1) and (1, {base:g})\n\n"
            "These functions are inverses. Their graphs mirror each other "
            "across the line y = x.")
    with right:
        st.pyplot(overview_figure(base))


def _tab_transformations(base, a, h, k):
    left, right = st.columns([1, 2.4])
    with left:
        st.markdown("**Show or hide curves**")
        for key, label, _ in CURVE_SWITCHES:
            st.checkbox(label, key=key)
    show = {key: st.session_state[key] for key, _, _ in CURVE_SWITCHES}
    with right:
        st.pyplot(transformations_figure(base, a, h, k, show))
        st.latex(log_latex(base, a, h, k))
        st.caption("Black = original logarithm. Blue = changed logarithm.")


def _tab_inverse(base, a, h, k):
    top_left, top_right = st.columns([3, 1])
    top_left.markdown("**A function and its inverse mirror across y = x.**")
    top_right.button("Emphasize transformed inverse", on_click=_emphasize_inverse)
    show = {key: st.session_state[key] for key, _, _ in CURVE_SWITCHES}
    st.pyplot(inverse_figure(base, a, h, k, show))
    if math.isclose(a, 0.0):
        st.info("When a = 0, the changed formula is a constant, so it does "
                "not have an inverse function.")
    else:
        st.latex(log_latex(base, a, h, k))
        st.latex(inverse_latex(base, a, h, k))
    st.caption("Use the checkboxes on the Transformations tab to choose "
               "which curves stand out.")


def _tab_bases():
    st.markdown("**Compare log base 2, log base 10, and the natural logarithm.**")
    st.pyplot(base_comparison_figure())
    rows = [(f"{x:g}", f"{math.log(x, 2):.3f}", f"{math.log10(x):.3f}",
             f"{math.log(x):.3f}") for x in (0.5, 1, 2, math.e, 10)]
    st.markdown(md_table(["x", "log₂(x)", "log₁₀(x)", "ln(x)"], rows))


def _tab_practice(base, a, h, k):
    left, right = st.columns([1, 2])
    with left:
        st.markdown("**Choose a question**")
        question = st.selectbox("Question", QUESTIONS, key="log_question",
                                label_visibility="collapsed")

        # Any change to the question or the function hides the old answer.
        signature = (question, base, a, h, k)
        if st.session_state.get("log_practice_sig") != signature:
            st.session_state.log_practice_sig = signature
            st.session_state.log_practice_view = "idle"

        if st.button("Show hint", key="log_hint_btn"):
            st.session_state.log_practice_view = "hint"
        if st.button("Reveal solution", key="log_solution_btn"):
            st.session_state.log_practice_view = "solution"
        st.button("Choose random settings", key="log_random_btn",
                  on_click=_random_settings)

    with right:
        st.markdown("**Current function**")
        st.latex(log_latex(base, a, h, k))
        st.markdown(f"**Question:** {question}?")
        st.pyplot(practice_figure(base, a, h, k))

        view = st.session_state.log_practice_view
        if view == "hint":
            st.info("**Hint:** " + HINTS[question])
        elif view == "solution":
            st.success(practice_solution(question, base, a, h, k))
        else:
            st.caption("When you are ready, choose Show hint or Reveal solution.")


def render():
    st.title("Project Logarithm")
    st.write("Explore logarithms, transformations, and inverse functions.")

    for key, value in DEFAULT_SETTINGS.items():
        st.session_state.setdefault(key, value)
    for key, _, default in CURVE_SWITCHES:
        st.session_state.setdefault(key, default)

    with st.expander("Function settings:  f(x) = a · log base b (x − h) + k",
                     expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        base = c1.number_input("Base b", min_value=0.05, max_value=100.0,
                               step=0.1, format="%g", key="log_base")
        a = c2.slider("Vertical scale a", -3.0, 3.0, step=0.1, key="log_a")
        h = c3.slider("Horizontal shift h", -5.0, 5.0, step=0.1, key="log_h")
        k = c4.slider("Vertical shift k", -5.0, 5.0, step=0.1, key="log_k")
        st.button("Reset settings", on_click=_reset_settings)

    if not is_valid_base(base):
        st.error("A logarithm's base must be greater than 0 and cannot be 1.")
        return

    tabs = st.tabs(["Overview", "Transformations", "Inverse & Reflection",
                    "Base Explorer", "Practice / Challenge"])
    with tabs[0]:
        _tab_overview(base)
    with tabs[1]:
        _tab_transformations(base, a, h, k)
    with tabs[2]:
        _tab_inverse(base, a, h, k)
    with tabs[3]:
        _tab_bases()
    with tabs[4]:
        _tab_practice(base, a, h, k)
