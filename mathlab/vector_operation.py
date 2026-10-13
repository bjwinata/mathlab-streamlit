"""Project Vector Operation - add, subtract, dot and cross products in 2-D and 3-D.

    * The dot product is a scalar (a number), not a vector.
    * A 2-D cross product is represented by its signed z-component.
    * A 3-D cross product is a vector perpendicular to both input vectors.
"""

import math

import streamlit as st
from matplotlib.figure import Figure

INK = "#172033"
MUTED = "#65718a"
VECTOR_A_COLOR = "#2563eb"
VECTOR_B_COLOR = "#e8792e"
RESULT_COLOR = "#0f9d78"

OPERATIONS = ["Addition (A + B)", "Subtraction (A - B)",
              "Dot product (A · B)", "Cross product (A × B)"]


# ======================================================================
# MATH
# ======================================================================

def add_vectors(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract_vectors(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot_product(a, b):
    """Multiply matching components, then add."""
    return sum(x * y for x, y in zip(a, b))


def cross_product_3d(a, b):
    ax, ay, az = a
    bx, by, bz = b
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)


def vector_length(vector):
    return math.sqrt(sum(component * component for component in vector))


def format_vector(vector):
    return "(" + ", ".join(f"{value:.3g}" for value in vector) + ")"


def angle_text(a, b):
    """Angle between two vectors, with a note when it is undefined."""
    length_product = vector_length(a) * vector_length(b)
    if length_product == 0:
        return "Angle is undefined because one vector has zero length."
    cosine = max(-1.0, min(1.0, dot_product(a, b) / length_product))
    return f"Angle between A and B: {math.degrees(math.acos(cosine)):.2f}°"


def padded_limits(values, minimum_span=4.0):
    """Plot limits that include the origin and leave room for the arrows."""
    low = min([0.0, *values])
    high = max([0.0, *values])
    padding = max(high - low, minimum_span) * 0.18
    return low - padding, high + padding


def operate_2d(a, b, operation):
    """Return (result_vector or None, list of result lines)."""
    if operation.startswith("Addition"):
        result = add_vectors(a, b)
        return result, [f"A + B = {format_vector(result)}"]
    if operation.startswith("Subtraction"):
        result = subtract_vectors(a, b)
        return result, [f"A - B = {format_vector(result)}"]
    if operation.startswith("Dot"):
        return None, [f"A · B = {dot_product(a, b):.4g}", angle_text(a, b)]
    z_value = a[0] * b[1] - a[1] * b[0]
    direction = ("out of the screen" if z_value > 0
                 else "into the screen" if z_value < 0 else "zero")
    return None, [f"A × B = {z_value:.4g} k",
                  f"Signed z-component: {z_value:.4g}",
                  f"Direction: {direction}",
                  "A 2-D cross product is not an in-plane arrow."]


def operate_3d(a, b, operation):
    if operation.startswith("Addition"):
        result = add_vectors(a, b)
        return result, [f"A + B = {format_vector(result)}"]
    if operation.startswith("Subtraction"):
        result = subtract_vectors(a, b)
        return result, [f"A - B = {format_vector(result)}"]
    if operation.startswith("Dot"):
        return None, [f"A · B = {dot_product(a, b):.4g}", angle_text(a, b)]
    result = cross_product_3d(a, b)
    return result, [f"A × B = {format_vector(result)}",
                    f"Length of result: {vector_length(result):.4g}",
                    "The result is perpendicular to A and B."]


# ======================================================================
# GRAPHS
# ======================================================================

def _arrow_2d(ax, vector, color, label, width=2.4):
    ax.annotate("", xy=vector, xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=width,
                                mutation_scale=14))
    if vector_length(vector) > 0:
        ax.annotate(label, vector, xytext=(6, 6), textcoords="offset points",
                    color=color, fontsize=9, fontweight="bold")


def figure_2d(a, b, operation, result):
    fig = Figure(figsize=(7.5, 5.8))
    ax = fig.add_subplot(111)
    ax.set_facecolor("#fbfcff")

    xs, ys = [a[0], b[0]], [a[1], b[1]]
    if result is not None:
        xs.append(result[0])
        ys.append(result[1])

    _arrow_2d(ax, a, VECTOR_A_COLOR, "A")
    _arrow_2d(ax, b, VECTOR_B_COLOR, "B")
    if result is not None:
        _arrow_2d(ax, result, RESULT_COLOR, f"Result {format_vector(result)}", 2.8)
        if operation.startswith("Addition"):      # tip-to-tail helper
            ax.annotate("", xy=(a[0] + b[0], a[1] + b[1]), xytext=a,
                        arrowprops=dict(arrowstyle="->", color=VECTOR_B_COLOR,
                                        lw=1.8, linestyle="--", alpha=0.8))

    ax.set_xlim(padded_limits(xs))
    ax.set_ylim(padded_limits(ys))
    ax.set_aspect("equal", adjustable="box")
    ax.axhline(0, color="#8a94a8", linewidth=1)
    ax.axvline(0, color="#8a94a8", linewidth=1)
    ax.grid(True, color="#dce3ef", linewidth=0.8)
    ax.set_xlabel("x", color=INK)
    ax.set_ylabel("y", color=INK)
    ax.set_title("2-D vector view", color=INK, fontsize=14, pad=12)
    ax.tick_params(colors=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b8c2d3")
    fig.tight_layout()
    return fig


def _arrow_3d(ax, vector, color, label):
    x, y, z = vector
    ax.quiver(0, 0, 0, x, y, z, color=color, arrow_length_ratio=0.12, linewidth=2.5)
    if vector_length(vector) > 0:
        ax.text(x, y, z, f"  {label}", color=color, fontsize=9)


def figure_3d(a, b, operation, result, azimuth, elevation):
    fig = Figure(figsize=(7.5, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#fbfcff")

    vectors = [a, b] + ([result] if result is not None else [])
    components = [c for vector in vectors for c in vector]
    lower, upper = padded_limits(components)

    _arrow_3d(ax, a, VECTOR_A_COLOR, "A")
    _arrow_3d(ax, b, VECTOR_B_COLOR, "B")
    if result is not None:
        _arrow_3d(ax, result, RESULT_COLOR, f"Result {format_vector(result)}")
        if operation.startswith("Addition"):      # tip-to-tail helper
            ax.quiver(a[0], a[1], a[2], b[0], b[1], b[2], color=VECTOR_B_COLOR,
                      linestyle="dashed", arrow_length_ratio=0.12,
                      linewidth=1.7, alpha=0.8)

    ax.set_xlim(lower, upper)
    ax.set_ylim(lower, upper)
    ax.set_zlim(lower, upper)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_xlabel("X", labelpad=8, color=INK)
    ax.set_ylabel("Y", labelpad=8, color=INK)
    ax.set_zlabel("Z", labelpad=8, color=INK)
    ax.set_title("3-D vector view", color=INK, pad=16)
    ax.tick_params(colors=MUTED, labelsize=8)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor((0.94, 0.96, 0.99, 1.0))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

def _vector_inputs(name, axes, defaults, prefix):
    """One number box per component of a vector."""
    st.markdown(f"**Vector {name}**")
    cols = st.columns(len(axes))
    return tuple(
        col.number_input(axis, value=default, step=1.0, format="%g",
                         key=f"{prefix}_{name}_{axis}")
        for col, axis, default in zip(cols, axes, defaults))


def _show_result(lines):
    st.success("\n\n".join(lines))


def _tab_2d():
    left, right = st.columns([1, 2])
    with left:
        a = _vector_inputs("A", "xy", (3.0, 2.0), "vec2")
        b = _vector_inputs("B", "xy", (1.0, 3.0), "vec2")
        operation = st.selectbox("Operation", OPERATIONS, key="vec2_op")
        result, lines = operate_2d(a, b, operation)
        _show_result(lines)
        st.caption("Tip: arrows start at (0, 0). For addition, the dashed "
                   "arrow shows the tip-to-tail idea.")
    with right:
        st.pyplot(figure_2d(a, b, operation, result))


def _tab_3d():
    left, right = st.columns([1, 2])
    with left:
        a = _vector_inputs("A", "xyz", (3.0, 2.0, 1.0), "vec3")
        b = _vector_inputs("B", "xyz", (1.0, 3.0, 2.0), "vec3")
        operation = st.selectbox("Operation", OPERATIONS, key="vec3_op")
        result, lines = operate_3d(a, b, operation)
        _show_result(lines)
        azimuth = st.slider("Rotate the view", -180, 180, -60, key="vec3_azim")
        elevation = st.slider("Tilt the view", -90, 90, 30, key="vec3_elev")
        st.caption("Use the sliders to rotate the 3-D graph. "
                   "The result vector is shown in green.")
    with right:
        st.pyplot(figure_3d(a, b, operation, result, azimuth, elevation))


def render():
    st.title("Project Vector Operation (2D / 3D)")
    st.write("Explore vector operations with interactive coordinate graphs.")
    tab_2d, tab_3d = st.tabs(["2-D Operations", "3-D Operations"])
    with tab_2d:
        _tab_2d()
    with tab_3d:
        _tab_3d()
