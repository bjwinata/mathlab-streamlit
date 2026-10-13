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
                     conic_sections, linear_inequality, logarithm, number_line,
                     parabola, polar_coordinates, vector_operation)

PAGES = {
    "parabola": parabola, "linear": linear_inequality, "abs": abs_inequality,
    "numberline": number_line, "square": completing_square,
    "interest": compound_interest, "log": logarithm,
    "vector": vector_operation, "polar": polar_coordinates, "conic": conic_sections,
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
    assert len(links) == len(PAGES), links
    assert len(st.pages) == len(PAGES) + 1
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

    # Vector Operation
    run("vector", vec2_op="Cross product (A × B)", vec3_op="Cross product (A × B)")
    run("vector", vec2_op="Dot product (A · B)", vec3_op="Dot product (A · B)")
    run("vector", vec2_op="Subtraction (A - B)", vec3_azim=40, vec3_elev=-20)
    run("vector", vec2_A_x=0.0, vec2_A_y=0.0, vec3_A_x=0.0, vec3_A_y=0.0, vec3_A_z=0.0)

    # Polar Coordinates: every family, every mode, bad input
    for family, (mode, equation, _) in polar_coordinates.FAMILY_PRESETS.items():
        run("polar", pol_family=family, pol_mode=mode, pol_equation=equation)
    run("polar", pol_mode=polar_coordinates.MODE_CARTESIAN, pol_equation="x**2 + y**2 - 4*x")
    run("polar", pol_equation="__import__('os').system('echo hacked')")
    run("polar", pol_equation="2*cos(")
    run("polar", pol_start=90.0, pol_end=10.0)
    run("polar", pol_display="Advanced", pol_grid=False, pol_equation="theta^2", pol_end=720.0)
    for choice in polar_coordinates.ANALYSES:
        run("polar", clicked=["Analyze"], pol_analysis_choice=choice)
        print("      ", choice, "->", st.session_state.pol_analysis_text.splitlines()[0][:70])

    # Conic Sections: bad inputs are explained, not crashed on
    run("conic", con_Circle_radius=-1.0, con_Parabola_p=0.0, con_Ellipse_a=0.0)
    run("conic", con_Parabola_direction="Horizontal", con_Ellipse_direction="Vertical",
        con_Hyperbola_direction="Vertical", con_Parabola_p=-3.0)
    run("conic", con_Ellipse_a=3.0, con_Ellipse_b=3.0, con_Circle_h=2.0, con_Circle_k=1.0)
    run_app()
    print("all pages rendered")

