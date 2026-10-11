"""Run every page's render() against a fake Streamlit and save the graphs.

    python tests/smoke_render.py

Useful for catching typos/exceptions without starting a server.  Pictures
land in /tmp/mathlab_shots.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fake_streamlit  # noqa: E402

st = fake_streamlit.install()

from mathlab import (abs_inequality, completing_square, compound_interest,  # noqa: E402
                     linear_inequality, logarithm, number_line, parabola)

PAGES = {
    "parabola": parabola, "linear": linear_inequality, "abs": abs_inequality,
    "numberline": number_line, "square": completing_square,
    "interest": compound_interest, "log": logarithm,
}


def run(name, clicked=(), **state):
    st.reset(name)
    st.session_state.update(state)
    st.clicked = set(clicked)
    PAGES[name].render()
    problems = st.texts("error") + st.texts("warning")
    print(f"ok  {name:11s} figures={st.figures} messages={problems}")


def run_app():
    """Execute app.py itself (navigation + home page)."""
    import runpy
    st.reset("app")
    runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"))
    links = st.texts("page_link")
    assert len(links) == 7, links
    assert len(st.pages) == 8
    print("ok  app.py      pages:", [p.title for p in st.pages])


if __name__ == "__main__":
    for page in PAGES:
        run(page)

    # A few awkward inputs
    run("parabola", par_a=-2.0, par_b=4.0, par_c=-5.0)        # complex roots
    run("parabola", par_a=1.0, par_b=-6.0, par_c=9.0)         # double root
    run("parabola", par_a=0.0)                                # not a parabola
    run("square", cts_a=2.0, cts_b=-8.0, cts_c=3.0)
    run("square", cts_a=1.0, cts_b=0.0, cts_c=4.0)
    run("linear", li_m1=1.0, li_b1=0.0, li_m2=1.0, li_b2=3.0)  # parallel
    run("abs", abs_combine="OR", abs_1_a=-1.0, abs_2_h=4.0)
    run("abs", abs_1_a=0.0)
    run("numberline", nl_combine="OR", nl_sign1="<", nl_sign2=">", nl_n1=-2.5, nl_n2=3.0)
    run("interest", ci_method="Continuous")
    run("log", log_base=0.5, log_a=-2.0, log_h=2.0, log_k=-1.0)
    run("log", log_base=1.0)                                  # invalid base
    run("log", clicked=["log_solution_btn"])
    run_app()
    print("all pages rendered")

