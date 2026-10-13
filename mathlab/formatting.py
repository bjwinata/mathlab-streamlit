"""Number and equation formatting shared by every project.

Equations are produced as LaTeX strings so they render nicely with
``st.latex`` (and, for the simple subset used here, as Matplotlib mathtext
in graph titles and legends).
"""

EPS = 1e-10

SIGN_LATEX = {">": ">", ">=": r"\geq", "<": "<", "<=": r"\leq"}


def fmt(value, digits=4):
    """2.0 -> '2', 3.5000 -> '3.5', -0.00001 -> '0'."""
    if value is None:
        return "N/A"
    if abs(value) < EPS:
        value = 0
    if float(value).is_integer():
        return str(int(value))
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def point(x, y, digits=4):
    return f"({fmt(x, digits)}, {fmt(y, digits)})"


def money(value):
    return f"${value:,.2f}"


def money_latex(value):
    return "\\$" + f"{value:,.2f}".replace(",", "{,}")


# ----------------------------------------------------------------------
# Building blocks for LaTeX expressions
# ----------------------------------------------------------------------

def _terms(pairs):
    """Join (coefficient, variable-text) pairs: skips zeros, hides unit
    coefficients, and handles signs  ->  '2x^{2} - x + 5'."""
    parts = []
    for coef, var in pairs:
        if abs(coef) < EPS:
            continue
        mag = abs(coef)
        body = var if (var and abs(mag - 1) < EPS) else fmt(mag) + var
        if not parts:
            parts.append(("-" if coef < 0 else "") + body)
        else:
            parts.append(("- " if coef < 0 else "+ ") + body)
    return " ".join(parts) if parts else "0"


def poly_latex(a, b, c):
    """a x^2 + b x + c"""
    return _terms([(a, "x^{2}"), (b, "x"), (c, "")])


def linear_latex(m, b):
    """m x + b"""
    return _terms([(m, "x"), (b, "")])


def lead_coeff(a):
    """Coefficient written in front of a bracket: 1 -> '', -1 -> '-', 3 -> '3'."""
    if abs(a - 1) < EPS:
        return ""
    if abs(a + 1) < EPS:
        return "-"
    return fmt(a)


def signed_const(v):
    """' + 5', ' - 2', or '' when v is zero."""
    if abs(v) < EPS:
        return ""
    return f" + {fmt(v)}" if v > 0 else f" - {fmt(-v)}"


def x_minus(h):
    """'x - 3', 'x + 3' or 'x'."""
    if abs(h) < EPS:
        return "x"
    return f"x - {fmt(h)}" if h > 0 else f"x + {fmt(-h)}"


def squared_binomial(h):
    """(x - h)^2, written as x^2 when h = 0."""
    if abs(h) < EPS:
        return "x^{2}"
    return f"({x_minus(h)})^{{2}}"


def vertex_form_latex(a, h, k):
    """y = a(x - h)^2 + k"""
    return f"y = {lead_coeff(a)}{squared_binomial(h)}{signed_const(k)}"


def factor_latex(r):
    """(x - r) for a root r."""
    return "x" if abs(r) < EPS else f"({x_minus(r)})"


def abs_latex(a, h, k):
    """a|x - h| + k"""
    return f"{lead_coeff(a)}|{x_minus(h)}|{signed_const(k)}"


def aligned(lines):
    """Stack several LaTeX lines so st.latex shows them as one block."""
    return "\\begin{aligned}" + " \\\\ ".join(lines) + "\\end{aligned}"


def md_table(headers, rows, escape_dollar=False):
    """Small Markdown table (wraps nicely on phones, never truncates)."""

    def clean(cell):
        text = str(cell).replace("|", "\\|")
        return text.replace("$", "\\$") if escape_dollar else text

    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(clean(c) for c in row) + " |" for row in rows]
    return "\n".join(out)
