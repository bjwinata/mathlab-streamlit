"""Math Lab - home page and navigation.

Run locally:   streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Math Lab", page_icon="📐", layout="wide")

from mathlab import (abs_inequality, completing_square, compound_interest,  # noqa: E402
                     conic_sections, linear_inequality, logarithm, number_line,
                     parabola, polar_coordinates, vector_operation)

COPYRIGHT = "© 2026 Jayden Winata"

# (module, sidebar title, url path, icon, one-line description)
PROJECTS = [
    (parabola, "Project Parabola", "parabola", "📈",
     "Vertex, roots, focus, directrix and a live graph for any quadratic."),
    (linear_inequality, "Project Linear Inequality", "linear-inequality", "📉",
     "Graph two linear inequalities and see where both are true."),
    (abs_inequality, "Project Compound Absolute Value", "absolute-value", "〰️",
     "Combine two absolute-value inequalities with AND / OR."),
    (number_line, "Project Compound Number Line", "number-line", "📏",
     "Combine two inequalities on aligned number lines."),
    (completing_square, "Project Completing the Square", "completing-the-square", "🟦",
     "Turn standard form into vertex form, step by step."),
    (compound_interest, "Project Compound Interest", "compound-interest", "💰",
     "Compare compounding methods with a growth graph and full working."),
    (logarithm, "Project Logarithm", "logarithm", "🔢",
     "Transformations, inverses, bases and practice questions."),
    (vector_operation, "Project Vector Operation (2D / 3D)", "vector-operation", "➡️",
     "Add, subtract, dot and cross products with 2D and 3D graphs."),
    (polar_coordinates, "Project Polar Coordinates", "polar-coordinates", "🌀",
     "Plot roses, limaçons and spirals, or type your own equation."),
    (conic_sections, "Project Conic Sections", "conic-sections", "⭕",
     "Circles, parabolas, ellipses and hyperbolas side by side."),
]


def home():
    st.title("MATH LAB")
    st.caption(COPYRIGHT)
    st.subheader("Choose a mathematics project")

    columns = st.columns(2)
    for index, page in enumerate(project_pages):
        description = PROJECTS[index][4]
        with columns[index % 2].container(border=True):
            st.page_link(page, label=f"**{page.title}**", icon=page.icon)
            st.caption(description)


home_page = st.Page(home, title="Home", icon="🏠", default=True)
project_pages = [
    st.Page(module.render, title=title, icon=icon, url_path=path)
    for module, title, path, icon, _ in PROJECTS
]

navigation = st.navigation([home_page] + project_pages)
st.sidebar.caption(COPYRIGHT)
navigation.run()
