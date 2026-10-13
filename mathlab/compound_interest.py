"""Project Compound Interest.

    A = P (1 + r/n)^(nt)      ordinary compounding
    A = P e^(rt)              continuous compounding

P = principal, r = annual rate (decimal), n = periods per year, t = years.
"""

import numpy as np
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from .formatting import aligned, fmt, md_table, money, money_latex

COMPOUNDING_PERIODS = {"Annual": 1, "Quarterly": 4, "Monthly": 12, "Daily": 365}
METHODS = ["Annual", "Quarterly", "Monthly", "Daily", "Continuous"]

RATE_SLIDER = (0.0, 20.0)
YEARS_SLIDER = (1.0, 50.0)


# ======================================================================
# MATH
# ======================================================================

def calculate_amount(principal, annual_rate, years, compounding):
    """Final balance.  ``years`` may be a number or a NumPy array."""
    if compounding == "Continuous":
        return principal * np.exp(annual_rate * years)
    n = COMPOUNDING_PERIODS[compounding]
    return principal * (1 + annual_rate / n) ** (n * years)


def calculate_all_methods(principal, annual_rate, years):
    return {m: float(calculate_amount(principal, annual_rate, years, m))
            for m in METHODS}


def solution_steps(principal, annual_rate, years, compounding):
    """List of (title, [LaTeX lines]) describing the calculation."""
    amount = float(calculate_amount(principal, annual_rate, years, compounding))
    interest = amount - principal
    P = money_latex(principal)

    identify = [
        f"P = {P}",
        f"r = {fmt(annual_rate * 100, 2)}\\% = {fmt(annual_rate, 6)}",
        f"t = {fmt(years)}\\ \\text{{years}}",
        f"\\text{{Compounding: {compounding}}}",
    ]
    interest_lines = [
        "\\text{Interest} = A - P",
        f"\\text{{Interest}} = {money_latex(amount)} - {P}",
        f"\\text{{Interest}} = {money_latex(interest)}",
    ]

    if compounding == "Continuous":
        return [
            ("STEP 1 — IDENTIFY THE VALUES", identify),
            ("STEP 2 — CHOOSE THE CONTINUOUS COMPOUNDING FORMULA",
             ["A = Pe^{rt}"]),
            ("STEP 3 — SUBSTITUTE THE VALUES",
             [f"A = {P} \\times e^{{({fmt(annual_rate, 6)})({fmt(years)})}}"]),
            ("STEP 4 — SIMPLIFY",
             [f"A = {P} \\times e^{{{fmt(annual_rate * years, 6)}}}"]),
            ("STEP 5 — CALCULATE", [f"A = {money_latex(amount)}"]),
            ("STEP 6 — CALCULATE INTEREST EARNED", interest_lines),
        ]

    n = COMPOUNDING_PERIODS[compounding]
    periodic = annual_rate / n
    periods = n * years
    return [
        ("STEP 1 — IDENTIFY THE VALUES", identify),
        ("STEP 2 — DETERMINE THE NUMBER OF COMPOUNDING PERIODS",
         [f"\\text{{{compounding} compounding means}}",
          f"n = {n}\\ \\text{{times per year}}"]),
        ("STEP 3 — WRITE THE COMPOUND INTEREST FORMULA",
         ["A = P\\left(1 + \\frac{r}{n}\\right)^{nt}"]),
        ("STEP 4 — SUBSTITUTE THE VALUES",
         [f"A = {P}\\left(1 + \\frac{{{fmt(annual_rate, 6)}}}{{{n}}}\\right)"
          f"^{{{n} \\times {fmt(years)}}}"]),
        ("STEP 5 — SIMPLIFY",
         [f"A = {P}\\left(1 + {fmt(periodic, 8)}\\right)^{{{fmt(periods, 6)}}}",
          f"A = {P} \\times {fmt(1 + periodic, 8)}^{{{fmt(periods, 6)}}}"]),
        ("STEP 6 — CALCULATE", [f"A = {money_latex(amount)}"]),
        ("STEP 7 — CALCULATE INTEREST EARNED", interest_lines),
    ]


def make_figure(principal, annual_rate, years, selected):
    times = np.linspace(0, years, 200)
    fig = Figure(figsize=(9, 5))
    ax = fig.add_subplot(111)
    for method in METHODS:
        balances = calculate_amount(principal, annual_rate, times, method)
        if method == selected:
            ax.plot(times, balances, linewidth=3, label=method)
        else:
            ax.plot(times, balances, linewidth=1.5, alpha=0.55, label=method)
    ax.set_title("Compound Interest Growth", fontsize=14, fontweight="bold")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Account Balance ($)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_xlim(0, years)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def _clamp(value, low, high):
    return max(low, min(high, value))


def _sync(source, target, low, high):
    """Keep a number box and its slider showing the same value."""
    st.session_state[target] = _clamp(st.session_state[source], low, high)


def _linked_input(label, name, box_range, box_step, slider_range, slider_step):
    """A number box plus a slider that always show the same value."""
    box_key, slider_key = f"ci_{name}_box", f"ci_{name}_slider"
    st.number_input(label, min_value=box_range[0], max_value=box_range[1],
                    step=box_step, format="%g", key=box_key,
                    on_change=_sync, args=(box_key, slider_key, *slider_range))
    st.slider(f"{label} slider", slider_range[0], slider_range[1],
              step=slider_step, key=slider_key, label_visibility="collapsed",
              on_change=_sync, args=(slider_key, box_key, *box_range))


def render():
    st.title("Project Compound Interest")
    st.write("See how money grows under different compounding methods.")

    # Initial values (set once; widgets then keep their own state)
    defaults = {"ci_principal": 10000.0, "ci_method": "Monthly",
                "ci_rate_box": 6.0, "ci_rate_slider": 6.0,
                "ci_years_box": 10.0, "ci_years_slider": 10.0}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    left, right = st.columns(2)
    with left:
        st.number_input("Principal ($)", min_value=0.01, max_value=1e12,
                        step=1000.0, format="%.2f", key="ci_principal")
        st.selectbox("Compounding", METHODS, key="ci_method")
    with right:
        _linked_input("Annual interest rate (%)", "rate",
                      box_range=(0.0, 100.0), box_step=0.1,
                      slider_range=RATE_SLIDER, slider_step=0.1)
        _linked_input("Time (years)", "years",
                      box_range=(0.1, 100.0), box_step=1.0,
                      slider_range=YEARS_SLIDER, slider_step=1.0)

    principal = st.session_state.ci_principal
    rate_percent = st.session_state.ci_rate_box
    years = st.session_state.ci_years_box
    compounding = st.session_state.ci_method
    annual_rate = rate_percent / 100

    amount = float(calculate_amount(principal, annual_rate, years, compounding))
    interest = amount - principal

    m1, m2, m3 = st.columns(3)
    m1.metric("Final balance", money(amount))
    m2.metric("Interest earned", money(interest))
    m3.metric("Principal", money(principal))

    st.pyplot(make_figure(principal, annual_rate, years, compounding))

    st.subheader("Compare all compounding methods")
    results = calculate_all_methods(principal, annual_rate, years)
    rows = []
    for method in METHODS:
        periods = COMPOUNDING_PERIODS.get(method, "∞")
        marker = "  ◀ selected" if method == compounding else ""
        rows.append((method + marker, periods, money(results[method]),
                     money(results[method] - principal)))
    st.markdown(md_table(["Method", "Periods / year", "Final balance",
                          "Interest earned"], rows, escape_dollar=True))

    st.subheader("Step-by-step solution")
    for title, lines in solution_steps(principal, annual_rate, years, compounding):
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.latex(aligned(lines))
