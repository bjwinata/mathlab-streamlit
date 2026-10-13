"""Project Conic Sections - circles, parabolas, ellipses and hyperbolas.

Each ``*_data`` function turns the inputs into a dictionary holding the
standard and expanded equations, a list of calculated properties, and what
the graph needs.  Invalid input raises ValueError with a readable message.
"""

import math

import numpy as np
import streamlit as st
from matplotlib.figure import Figure

KINDS = ["Circle", "Parabola", "Ellipse", "Hyperbola"]
COMPARE_COLORS = {"Circle": "tab:blue", "Parabola": "tab:green",
                  "Ellipse": "tab:purple", "Hyperbola": "tab:orange"}


# ======================================================================
# FORMATTING
# ======================================================================

def number_text(value, digits=3):
    """Format a number neatly, avoiding unnecessary trailing zeroes."""
    if value is None:
        return "not applicable"
    if isinstance(value, complex):
        return f"{value.real:.{digits}g} {value.imag:+.{digits}g}i"
    if not math.isfinite(value):
        return "not applicable"
    if abs(value) < 1e-10:
        value = 0.0
    return f"{value:.{digits}g}"


def signed_number(value):
    return f"+ {number_text(value)}" if value >= 0 else f"- {number_text(abs(value))}"



def squared(variable, center):
    """'x²' when the center is 0, otherwise '(x - 3)²'."""
    if abs(center) < 1e-10:
        return f"{variable}²"
    return f"({variable} {signed_number(-center)})²"


def shifted(variable, center):
    """'y' when the center is 0, otherwise '(y - 3)'."""
    if abs(center) < 1e-10:
        return variable
    return f"({variable} {signed_number(-center)})"


def coefficient(value):
    """Number written in front of something: 1 -> '', -1 -> '-'."""
    if abs(value - 1) < 1e-9:
        return ""
    if abs(value + 1) < 1e-9:
        return "-"
    return number_text(value)


def expanded_text(terms):
    """Join (coefficient, symbol) pairs into 'x² + y² - 8x - 4 = 0'.
    Zero terms are skipped; the constant term uses the symbol ''."""
    text = ""
    for value, symbol in terms:
        if abs(value) < 1e-10:
            continue
        if symbol:
            body = coefficient(abs(value)) + symbol
        else:
            body = number_text(abs(value))
        if not text:
            text = ("-" if value < 0 else "") + body
        else:
            text += (" - " if value < 0 else " + ") + body
    return (text or "0") + " = 0"


def unique_points(points, tolerance=1e-7):
    """Drop duplicate points that can arise from numerical calculations."""
    answer = []
    for point in points:
        if point is None or not all(math.isfinite(v) for v in point):
            continue
        if not any(math.dist(point, old) < tolerance for old in answer):
            answer.append(point)
    return answer


def format_intercepts(points):
    if not points:
        return "none"
    return ", ".join(f"({number_text(x)}, {number_text(y)})"
                     for x, y in unique_points(points))


# ======================================================================
# MATH: one function per conic
# ======================================================================

def circle_x_intercepts(h, k, radius):
    inside = radius * radius - k * k
    if inside < -1e-9:
        return []
    if abs(inside) <= 1e-9:
        return [(h, 0.0)]
    offset = math.sqrt(inside)
    return [(h - offset, 0.0), (h + offset, 0.0)]


def circle_y_intercepts(h, k, radius):
    inside = radius * radius - h * h
    if inside < -1e-9:
        return []
    if abs(inside) <= 1e-9:
        return [(0.0, k)]
    offset = math.sqrt(inside)
    return [(0.0, k - offset), (0.0, k + offset)]


def circle_data(h, k, radius):
    if radius <= 0:
        raise ValueError("The radius must be greater than zero.")
    equation = f"{squared('x', h)} + {squared('y', k)} = {number_text(radius ** 2)}"
    expanded = expanded_text([(1, "x²"), (1, "y²"), (-2 * h, "x"), (-2 * k, "y"),
                              (h * h + k * k - radius * radius, "")])
    properties = [
        f"Center: ({number_text(h)}, {number_text(k)})",
        f"Radius: {number_text(radius)}",
        f"Diameter: {number_text(2 * radius)}",
        f"Circumference: {number_text(2 * math.pi * radius)}",
        f"Area: {number_text(math.pi * radius ** 2)}",
        "Eccentricity: 0 (a circle is the special case of an ellipse)",
        f"Left / right points: ({number_text(h - radius)}, {number_text(k)}) "
        f"and ({number_text(h + radius)}, {number_text(k)})",
        f"Bottom / top points: ({number_text(h)}, {number_text(k - radius)}) "
        f"and ({number_text(h)}, {number_text(k + radius)})",
        f"x-intercepts: {format_intercepts(circle_x_intercepts(h, k, radius))}",
        f"y-intercepts: {format_intercepts(circle_y_intercepts(h, k, radius))}",
        f"Domain: [{number_text(h - radius)}, {number_text(h + radius)}]",
        f"Range: [{number_text(k - radius)}, {number_text(k + radius)}]",
    ]
    return {"kind": "Circle", "equation": equation, "expanded": expanded,
            "properties": properties, "center": (h, k), "radius": radius}


def parabola_data(h, k, p, direction):
    if p == 0:
        raise ValueError("p cannot be zero. It controls the parabola's "
                         "width and direction.")
    latus = abs(4 * p)
    if direction == "Vertical":
        equation = f"{squared('x', h)} = {coefficient(4 * p)}{shifted('y', k)}"
        expanded = expanded_text([(1, "x²"), (-2 * h, "x"), (-4 * p, "y"),
                                  (h * h + 4 * p * k, "")])
        focus = (h, k + p)
        directrix = f"y = {number_text(k - p)}"
        axis = f"x = {number_text(h)}"
        direction_text = "opens upward" if p > 0 else "opens downward"
        points = [(h - latus / 2, k + p), (h + latus / 2, k + p)]
        value = -4 * p * k
        x_intercepts = []
        if value >= 0:
            root = math.sqrt(value)
            x_intercepts = [(h - root, 0.0), (h + root, 0.0)]
        if abs(value) < 1e-9:
            x_intercepts = [(h, 0.0)]
        y_intercepts = [(0.0, k + (h * h) / (4 * p))]
        domain = "all real x"
        range_text = f"y ≥ {number_text(k)}" if p > 0 else f"y ≤ {number_text(k)}"
    else:
        equation = f"{squared('y', k)} = {coefficient(4 * p)}{shifted('x', h)}"
        expanded = expanded_text([(1, "y²"), (-2 * k, "y"), (-4 * p, "x"),
                                  (k * k + 4 * p * h, "")])
        focus = (h + p, k)
        directrix = f"x = {number_text(h - p)}"
        axis = f"y = {number_text(k)}"
        direction_text = "opens right" if p > 0 else "opens left"
        points = [(h + p, k - latus / 2), (h + p, k + latus / 2)]
        value = -4 * p * h
        y_intercepts = []
        if value >= 0:
            root = math.sqrt(value)
            y_intercepts = [(0.0, k - root), (0.0, k + root)]
        if abs(value) < 1e-9:
            y_intercepts = [(0.0, k)]
        x_intercepts = [(h + (k * k) / (4 * p), 0.0)]
        domain = f"x ≥ {number_text(h)}" if p > 0 else f"x ≤ {number_text(h)}"
        range_text = "all real y"
    properties = [
        f"Vertex: ({number_text(h)}, {number_text(k)})",
        f"Focus: ({number_text(focus[0])}, {number_text(focus[1])})",
        f"Axis of symmetry: {axis}",
        f"Directrix: {directrix}",
        f"Parameter p: {number_text(p)}",
        f"Direction: {direction_text}",
        f"Latus rectum length: {number_text(latus)}",
        f"Latus rectum endpoints: {format_intercepts(points)}",
        f"x-intercepts: {format_intercepts(x_intercepts)}",
        f"y-intercepts: {format_intercepts(y_intercepts)}",
        f"Domain: {domain}",
        f"Range: {range_text}",
        "Eccentricity: 1",
    ]
    return {"kind": "Parabola", "equation": equation, "expanded": expanded,
            "properties": properties, "center": (h, k), "p": p,
            "direction": direction}


def ellipse_directrices(h, k, major, eccentricity, major_axis):
    if eccentricity < 1e-9:
        return "not applicable for a circle"
    distance = major / eccentricity
    if major_axis == "horizontal":
        return f"x = {number_text(h - distance)} and x = {number_text(h + distance)}"
    return f"y = {number_text(k - distance)} and y = {number_text(k + distance)}"


def ellipse_x_intercepts(h, k, horizontal_radius, vertical_radius):
    """Where an ellipse crosses y = 0."""
    factor = 1 - (k * k) / (vertical_radius * vertical_radius)
    if factor < -1e-9:
        return []
    if abs(factor) <= 1e-9:
        return [(h, 0.0)]
    offset = horizontal_radius * math.sqrt(factor)
    return [(h - offset, 0.0), (h + offset, 0.0)]


def ellipse_y_intercepts(h, k, horizontal_radius, vertical_radius):
    """Where an ellipse crosses x = 0."""
    factor = 1 - (h * h) / (horizontal_radius * horizontal_radius)
    if factor < -1e-9:
        return []
    if abs(factor) <= 1e-9:
        return [(0.0, k)]
    offset = vertical_radius * math.sqrt(factor)
    return [(0.0, k - offset), (0.0, k + offset)]


def ellipse_data(h, k, a, b, direction):
    if a <= 0 or b <= 0:
        raise ValueError("Both ellipse semi-axis lengths a and b must be "
                         "greater than zero.")
    note = "This ellipse is a circle because a = b." if abs(a - b) < 1e-9 else None
    major, minor = max(a, b), min(a, b)
    c = math.sqrt(abs(a * a - b * b))
    e = c / major
    if direction == "Horizontal":
        equation = (f"{squared('x', h)}/{number_text(a * a)} + "
                    f"{squared('y', k)}/{number_text(b * b)} = 1")
        expanded = expanded_text([
            (b * b, "x²"), (a * a, "y²"), (-2 * h * b * b, "x"), (-2 * k * a * a, "y"),
            (h * h * b * b + k * k * a * a - a * a * b * b, "")])
        if a >= b:
            major_axis = "horizontal"
            vertices, covertices = [(h - a, k), (h + a, k)], [(h, k - b), (h, k + b)]
            foci = [(h - c, k), (h + c, k)]
        else:
            major_axis = "vertical"
            vertices, covertices = [(h, k - b), (h, k + b)], [(h - a, k), (h + a, k)]
            foci = [(h, k - c), (h, k + c)]
        horizontal_radius, vertical_radius = a, b
    else:
        equation = (f"{squared('x', h)}/{number_text(b * b)} + "
                    f"{squared('y', k)}/{number_text(a * a)} = 1")
        expanded = expanded_text([
            (a * a, "x²"), (b * b, "y²"), (-2 * h * a * a, "x"), (-2 * k * b * b, "y"),
            (h * h * a * a + k * k * b * b - a * a * b * b, "")])
        if a >= b:
            major_axis = "vertical"
            vertices, covertices = [(h, k - a), (h, k + a)], [(h - b, k), (h + b, k)]
            foci = [(h, k - c), (h, k + c)]
        else:
            major_axis = "horizontal"
            vertices, covertices = [(h - b, k), (h + b, k)], [(h, k - a), (h, k + a)]
            foci = [(h - c, k), (h + c, k)]
        horizontal_radius, vertical_radius = b, a
    perimeter = math.pi * (3 * (major + minor)
                           - math.sqrt((3 * major + minor) * (major + 3 * minor)))
    properties = [
        f"Center: ({number_text(h)}, {number_text(k)})",
        f"Major-axis direction: {major_axis}",
        f"Semi-axis lengths: {number_text(major)} and {number_text(minor)}",
        f"Major-axis length: {number_text(2 * major)}",
        f"Minor-axis length: {number_text(2 * minor)}",
        f"Focal distance c: {number_text(c)}",
        f"Eccentricity: {number_text(e)}",
        f"Vertices: {format_intercepts(vertices)}",
        f"Co-vertices: {format_intercepts(covertices)}",
        f"Foci: {format_intercepts(foci)}",
        f"Directrices: {ellipse_directrices(h, k, major, e, major_axis)}",
        f"Approximate perimeter: {number_text(perimeter)}",
        f"Area: {number_text(math.pi * a * b)}",
        f"x-intercepts: {format_intercepts(ellipse_x_intercepts(h, k, horizontal_radius, vertical_radius))}",
        f"y-intercepts: {format_intercepts(ellipse_y_intercepts(h, k, horizontal_radius, vertical_radius))}",
        f"Domain: [{number_text(h - horizontal_radius)}, {number_text(h + horizontal_radius)}]",
        f"Range: [{number_text(k - vertical_radius)}, {number_text(k + vertical_radius)}]",
    ]
    if note:
        properties.insert(1, note)
    return {"kind": "Ellipse", "equation": equation, "expanded": expanded,
            "properties": properties, "center": (h, k), "a": a, "b": b,
            "direction": direction}


def hyperbola_data(h, k, a, b, direction):
    if a <= 0 or b <= 0:
        raise ValueError("Both hyperbola parameters a and b must be greater "
                         "than zero.")
    c = math.sqrt(a * a + b * b)
    e = c / a
    if direction == "Horizontal":
        equation = (f"{squared('x', h)}/{number_text(a * a)} - "
                    f"{squared('y', k)}/{number_text(b * b)} = 1")
        expanded = expanded_text([
            (b * b, "x²"), (-a * a, "y²"), (-2 * h * b * b, "x"), (2 * k * a * a, "y"),
            (h * h * b * b - k * k * a * a - a * a * b * b, "")])
        vertices, foci = [(h - a, k), (h + a, k)], [(h - c, k), (h + c, k)]
        slope = b / a
        directrices = f"x = {number_text(h - a / e)} and x = {number_text(h + a / e)}"
        axis = "horizontal"
    else:
        equation = (f"{squared('y', k)}/{number_text(a * a)} - "
                    f"{squared('x', h)}/{number_text(b * b)} = 1")
        expanded = expanded_text([
            (-a * a, "x²"), (b * b, "y²"), (2 * h * a * a, "x"), (-2 * k * b * b, "y"),
            (k * k * b * b - h * h * a * a - a * a * b * b, "")])
        vertices, foci = [(h, k - a), (h, k + a)], [(h, k - c), (h, k + c)]
        slope = a / b
        directrices = f"y = {number_text(k - a / e)} and y = {number_text(k + a / e)}"
        axis = "vertical"
    asymptotes = [f"y = {number_text(k)} + ({number_text(slope)})(x - {number_text(h)})",
                  f"y = {number_text(k)} - ({number_text(slope)})(x - {number_text(h)})"]
    properties = [
        f"Center: ({number_text(h)}, {number_text(k)})",
        f"Transverse axis: {axis}",
        f"Vertices: {format_intercepts(vertices)}",
        f"Foci: {format_intercepts(foci)}",
        f"c = √(a² + b²): {number_text(c)}",
        f"Eccentricity: {number_text(e)} (always greater than 1)",
        f"Conjugate-axis length: {number_text(2 * b)}",
        f"Transverse-axis length: {number_text(2 * a)}",
        f"Asymptotes: {asymptotes[0]} ; {asymptotes[1]}",
        f"Directrices: {directrices}",
        "Latus rectum length: " + number_text(2 * b * b / a),
        "x-intercepts: computed from the graph equation; may be none",
        "y-intercepts: computed from the graph equation; may be none",
        "Domain: two separate intervals for a horizontal hyperbola; "
        "all real x for a vertical hyperbola",
        "Range: all real y for a horizontal hyperbola; "
        "two separate intervals for a vertical hyperbola",
    ]
    return {"kind": "Hyperbola", "equation": equation, "expanded": expanded,
            "properties": properties, "center": (h, k), "a": a, "b": b,
            "direction": direction, "c": c}


def build_data(kind, values, direction):
    """Call the right *_data function (``values`` are plain numbers)."""
    if kind == "Circle":
        return circle_data(values["h"], values["k"], values["radius"])
    if kind == "Parabola":
        return parabola_data(values["h"], values["k"], values["p"], direction)
    if kind == "Ellipse":
        return ellipse_data(values["h"], values["k"], values["a"], values["b"], direction)
    return hyperbola_data(values["h"], values["k"], values["a"], values["b"], direction)


# ======================================================================
# GRAPHS
# ======================================================================

def draw_conic(axis, data, color="tab:blue", label=None):
    """Draw a conic with simple parametric formulas."""
    h, k = data["center"]
    kind = data["kind"]
    axis.axhline(0, color="gray", linewidth=0.8)
    axis.axvline(0, color="gray", linewidth=0.8)
    axis.grid(True, alpha=0.25)
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_aspect("equal", adjustable="box")

    if kind == "Circle":
        radius = data["radius"]
        angle = np.linspace(0, 2 * np.pi, 600)
        axis.plot(h + radius * np.cos(angle), k + radius * np.sin(angle),
                  color=color, linewidth=2.2, label=label or "Circle")
        axis.scatter([h], [k], color=color, s=25, zorder=4)

    elif kind == "Ellipse":
        a, b = data["a"], data["b"]
        angle = np.linspace(0, 2 * np.pi, 600)
        rx, ry = (a, b) if data["direction"] == "Horizontal" else (b, a)
        axis.plot(h + rx * np.cos(angle), k + ry * np.sin(angle),
                  color=color, linewidth=2.2, label=label or "Ellipse")
        axis.scatter([h], [k], color=color, s=25, zorder=4)

    elif kind == "Parabola":
        p, direction = data["p"], data["direction"]
        reach = max(8.0, 4 * abs(p) + 2)   # long enough for the whole view
        t = np.linspace(-reach, reach, 600)
        if direction == "Vertical":
            axis.plot(h + t, k + (t * t) / (4 * p), color=color, linewidth=2.2,
                      label=label or "Parabola")
            axis.axhline(k - p, color=color, linestyle=":", alpha=0.75, label="Directrix")
            axis.scatter([h], [k + p], color="tab:red", s=30, label="Focus")
        else:
            axis.plot(h + (t * t) / (4 * p), k + t, color=color, linewidth=2.2,
                      label=label or "Parabola")
            axis.axvline(h - p, color=color, linestyle=":", alpha=0.75, label="Directrix")
            axis.scatter([h + p], [k], color="tab:red", s=30, label="Focus")
        axis.scatter([h], [k], color=color, s=30, zorder=4)

    elif kind == "Hyperbola":
        a, b, direction = data["a"], data["b"], data["direction"]
        t = np.linspace(-2.8, 2.8, 600)
        if direction == "Horizontal":
            y = k + b * np.sinh(t)
            axis.plot(h + a * np.cosh(t), y, color=color, linewidth=2.2,
                      label=label or "Hyperbola")
            axis.plot(h - a * np.cosh(t), y, color=color, linewidth=2.2)
            x_line = np.linspace(h - 2.8 * a, h + 2.8 * a, 300)
            slope = b / a
            vertices_x, vertices_y = [h - a, h + a], [k, k]
        else:
            x = h + b * np.sinh(t)
            axis.plot(x, k + a * np.cosh(t), color=color, linewidth=2.2,
                      label=label or "Hyperbola")
            axis.plot(x, k - a * np.cosh(t), color=color, linewidth=2.2)
            x_line = np.linspace(h - 2.8 * b, h + 2.8 * b, 300)
            slope = a / b
            vertices_x, vertices_y = [h, h], [k - a, k + a]
        axis.plot(x_line, k + slope * (x_line - h), color="tab:orange",
                  linestyle=":", label="Asymptotes")
        axis.plot(x_line, k - slope * (x_line - h), color="tab:orange", linestyle=":")
        axis.scatter(vertices_x, vertices_y, color="tab:red", s=30, label="Vertices")

    axis.legend(loc="best", fontsize=8)


def view_limits(data):
    """A useful window around one conic, with room for its features."""
    h, k = data["center"]
    kind = data["kind"]
    if kind == "Circle":
        r = data["radius"]
        pad = max(1.0, r * 0.35)
        limits = (h - r - pad, h + r + pad, k - r - pad, k + r + pad)
    elif kind == "Ellipse":
        a, b = data["a"], data["b"]
        rx, ry = (a, b) if data["direction"] == "Horizontal" else (b, a)
        limits = (h - 1.35 * rx - 0.5, h + 1.35 * rx + 0.5,
                  k - 1.35 * ry - 0.5, k + 1.35 * ry + 0.5)
    elif kind == "Parabola":
        p = abs(data["p"])
        span = max(6.0, 4 * p)
        extent = max(6.0, span * span / (4 * p))
        if data["direction"] == "Vertical":
            limits = (h - span, h + span, k - extent * 0.25, k + extent)
        else:
            limits = (h - extent * 0.25, h + extent, k - span, k + span)
    else:
        a, b = data["a"], data["b"]
        if data["direction"] == "Horizontal":
            limits = (h - 2.8 * a, h + 2.8 * a, k - 2.8 * b, k + 2.8 * b)
        else:
            limits = (h - 2.8 * b, h + 2.8 * b, k - 2.8 * a, k + 2.8 * a)
    x_min, x_max, y_min, y_max = limits
    if x_max - x_min < 1:
        x_min, x_max = h - 1, h + 1
    if y_max - y_min < 1:
        y_min, y_max = k - 1, k + 1
    return x_min, x_max, y_min, y_max


def conic_figure(data):
    fig = Figure(figsize=(7, 4.7), constrained_layout=True)
    axis = fig.add_subplot(111)
    draw_conic(axis, data)
    x_min, x_max, y_min, y_max = view_limits(data)
    axis.set_xlim(x_min, x_max)
    axis.set_ylim(y_min, y_max)
    return fig


def compare_figure(all_data):
    """All valid conics on one set of axes (``all_data``: {kind: data})."""
    fig = Figure(figsize=(8, 6), constrained_layout=True)
    axis = fig.add_subplot(111)
    xs, ys = [], []
    for kind, data in all_data.items():
        draw_conic(axis, data, color=COMPARE_COLORS[kind], label=kind)
        h, k = data["center"]
        if kind == "Circle":
            rx = ry = data["radius"]
        elif kind == "Ellipse":
            horizontal = data["direction"] == "Horizontal"
            rx = data["a"] if horizontal else data["b"]
            ry = data["b"] if horizontal else data["a"]
        elif kind == "Parabola":
            rx = ry = max(4.0, abs(data["p"]) * 3)
        else:
            horizontal = data["direction"] == "Horizontal"
            rx = data["a"] * 2.5 if horizontal else data["b"] * 2.5
            ry = data["b"] * 2.5 if horizontal else data["a"] * 2.5
        xs += [h - rx, h + rx]
        ys += [k - ry, k + ry]
    if xs:
        x_pad = max(2, (max(xs) - min(xs)) * 0.12)
        y_pad = max(2, (max(ys) - min(ys)) * 0.12)
        axis.set_xlim(min(xs) - x_pad, max(xs) + x_pad)
        axis.set_ylim(min(ys) - y_pad, max(ys) + y_pad)
    return fig


# ======================================================================
# STREAMLIT PAGE
# ======================================================================

# (value key, label, default) for each conic's number boxes
FIELDS = {
    "Circle": [("h", "Center x (h)", 0.0), ("k", "Center y (k)", 0.0),
               ("radius", "Radius r (> 0)", 4.0)],
    "Parabola": [("h", "Vertex x (h)", 0.0), ("k", "Vertex y (k)", 0.0),
                 ("p", "Parameter p (not 0)", 1.0)],
    "Ellipse": [("h", "Center x (h)", 0.0), ("k", "Center y (k)", 0.0),
                ("a", "Semi-axis / parameter a (> 0)", 4.0),
                ("b", "Semi-axis / parameter b (> 0)", 2.0)],
    "Hyperbola": [("h", "Center x (h)", 0.0), ("k", "Center y (k)", 0.0),
                  ("a", "Semi-axis / parameter a (> 0)", 4.0),
                  ("b", "Semi-axis / parameter b (> 0)", 2.0)],
}
DIRECTIONS = {   # label, options
    "Parabola": ("Opening direction", ["Vertical", "Horizontal"]),
    "Ellipse": ("Major-axis direction", ["Horizontal", "Vertical"]),
    "Hyperbola": ("Transverse-axis direction", ["Horizontal", "Vertical"]),
}

FORMULA_GUIDE = [
    ("Circle", r"(x - h)^2 + (y - k)^2 = r^2",
     "Center (h, k); every point is distance r from the center."),
    ("Vertical parabola", r"(x - h)^2 = 4p(y - k)",
     "Vertex (h, k); p is the signed distance from vertex to focus."),
    ("Horizontal parabola", r"(y - k)^2 = 4p(x - h)",
     "Positive p opens right; negative p opens left."),
    ("Horizontal ellipse", r"\frac{(x - h)^2}{a^2} + \frac{(y - k)^2}{b^2} = 1",
     "The ellipse is closed; the longer semi-axis is the major axis."),
    ("Horizontal hyperbola", r"\frac{(x - h)^2}{a^2} - \frac{(y - k)^2}{b^2} = 1",
     "The branches open left and right and approach two asymptotes."),
    ("Vertical hyperbola", r"\frac{(y - k)^2}{a^2} - \frac{(x - h)^2}{b^2} = 1",
     "The branches open up and down and approach two asymptotes."),
]


def _conic_tab(kind):
    """Inputs on the left, graph and properties on the right.
    Returns the calculated data, or None when the input is invalid."""
    left, right = st.columns([1, 2.4])
    with left:
        st.subheader(f"{kind} settings")
        values = {key: st.number_input(label, value=default, step=1.0,
                                       format="%g", key=f"con_{kind}_{key}")
                  for key, label, default in FIELDS[kind]}
        direction = None
        if kind in DIRECTIONS:
            label, options = DIRECTIONS[kind]
            direction = st.selectbox(label, options, key=f"con_{kind}_direction")

    try:
        data = build_data(kind, values, direction)
    except ValueError as error:
        right.error(f"Check your input: {error}")
        return None

    with right:
        st.markdown(f"**Standard form:** {data['equation']}")
        st.markdown(f"**Expanded form:** {data['expanded']}")
        st.pyplot(conic_figure(data))
        st.markdown("**Calculated properties**")
        st.markdown("\n".join("- " + line for line in data["properties"]))
    return data


def render():
    st.title("Project Conic Sections")
    st.write("Explore how changing parameters changes the equation, "
             "properties, and graph.")

    tabs = st.tabs(KINDS + ["Compare Conics", "Formula Guide"])
    results = {}
    for tab, kind in zip(tabs, KINDS):
        with tab:
            data = _conic_tab(kind)
            if data is not None:
                results[kind] = data

    with tabs[4]:
        st.subheader("Compare the four conic families")
        st.write("This view uses the current settings from the four tabs. "
                 "Choose a tab to edit a conic, then return here to compare them.")
        st.pyplot(compare_figure(results))

    with tabs[5]:
        st.subheader("Conic-section formula guide")
        for name, formula, explanation in FORMULA_GUIDE:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.latex(formula)
                st.caption(explanation)
        st.caption("Note: a and b have different meanings in different conic "
                   "forms. Read the selected tab's labels carefully. Expanded "
                   "forms are shown algebraically; they are not automatically "
                   "rearranged into a single Ax² + By² + Cx + Dy + E = 0 format.")
