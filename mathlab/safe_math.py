"""Read equations typed by a user - safely.

Why this exists
---------------
SymPy's ``sympify`` runs Python's ``eval`` behind the scenes.  That is fine
on your own computer, but on a public website a visitor could type Python
code instead of an equation.  This module instead:

1. parses the text with ``ast.parse`` (parsing never runs anything),
2. checks every part of the tree against a short allow-list
   (numbers, + - * / **, the variables r/theta/x/y, and a few functions),
3. evaluates the tree itself with NumPy, or builds a SymPy expression from it.

Anything else (attribute access, imports, lambdas, strings, huge powers...)
is rejected with a friendly message.

    2*cos(3*theta)      r**2 - 4*cos(2*theta)      x**2 + y**2 - 4*x
"""

import ast
import math

import numpy as np
import sympy as sp

MAX_LENGTH = 150          # characters
MAX_NODES = 80            # pieces of the expression
MAX_ANALYSIS_NODES = 40   # symbolic work (simplify, diff) is heavier
MAX_NUMBER = 1e15
MAX_EXPONENT = 1000
MAX_POWER_BITS = 3000     # keeps exact integer powers small

r_symbol, theta_symbol = sp.symbols("r theta", real=True)
x_symbol, y_symbol = sp.symbols("x y", real=True)
SYMBOLS = {"r": r_symbol, "theta": theta_symbol, "x": x_symbol, "y": y_symbol}

FUNCTIONS = {            # name: (NumPy version, SymPy version)
    "sin": (np.sin, sp.sin), "cos": (np.cos, sp.cos), "tan": (np.tan, sp.tan),
    "asin": (np.arcsin, sp.asin), "acos": (np.arccos, sp.acos),
    "atan": (np.arctan, sp.atan), "sqrt": (np.sqrt, sp.sqrt),
    "abs": (np.abs, sp.Abs), "exp": (np.exp, sp.exp), "log": (np.log, sp.log),
}
CONSTANTS = {"pi": (math.pi, sp.pi), "E": (math.e, sp.E)}

_BINARY = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_UNARY = (ast.UAdd, ast.USub)

SYNTAX_MESSAGE = ("I could not read that expression. Check parentheses, "
                  "function names, and multiplication signs (use * and **).")


class Equation:
    """A validated expression, ready to evaluate or convert to SymPy."""

    def __init__(self, tree, variables, node_count):
        self._tree = tree
        self.variables = variables          # names such as {'theta'}
        self.node_count = node_count

    # -- numbers ------------------------------------------------------
    def evaluate(self, **values):
        """Evaluate with NumPy.  Pass arrays, e.g. ``evaluate(theta=angles)``."""
        with np.errstate(all="ignore"):
            return _evaluate(self._tree, values)

    # -- symbols ------------------------------------------------------
    def to_sympy(self):
        if self.node_count > MAX_ANALYSIS_NODES:
            raise ValueError("This equation is too long for symbolic analysis. "
                             "Try a shorter one.")
        return _to_sympy(self._tree)


def parse_equation(text, allowed_variables):
    """Validate ``text`` and return an :class:`Equation`.

    ``allowed_variables`` is the set of names this equation type may use,
    for example ``{"theta"}`` or ``{"x", "y"}``.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Please enter an equation.")
    if len(text) > MAX_LENGTH:
        raise ValueError(f"Please keep the equation under {MAX_LENGTH} characters.")

    try:
        tree = ast.parse(text.replace("^", "**"), mode="eval")
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        raise ValueError(SYNTAX_MESSAGE) from None

    node_count = sum(1 for _ in ast.walk(tree))
    if node_count > MAX_NODES:
        raise ValueError("That equation is too complicated. Please simplify it.")

    used, unknown = set(), set()
    _validate(tree.body, used, unknown)
    if unknown:
        raise ValueError("Unsupported symbol(s): " + ", ".join(sorted(unknown)))
    wrong = used - set(allowed_variables)
    if wrong:
        raise ValueError(
            f"This equation type can only use {_names(allowed_variables)}, "
            f"but the equation contains {_names(wrong)}.")
    return Equation(tree.body, used, node_count)


def _names(names):
    return ", ".join(sorted(names, key=str))


# ----------------------------------------------------------------------
# Validation: walk the tree once and reject everything not on the list
# ----------------------------------------------------------------------

def _validate(node, used, unknown):
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Only numbers are allowed in an equation.")
        if not math.isfinite(value) or abs(value) > MAX_NUMBER:
            raise ValueError("Numbers must be smaller than 1e15.")
    elif isinstance(node, ast.Name):
        if node.id in SYMBOLS:
            used.add(node.id)
        elif node.id in FUNCTIONS:
            raise ValueError(f"'{node.id}' is a function: write {node.id}(...).")
        elif node.id not in CONSTANTS:
            unknown.add(node.id)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, _BINARY):
        _validate(node.left, used, unknown)
        _validate(node.right, used, unknown)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, _UNARY):
        _validate(node.operand, used, unknown)
    elif isinstance(node, ast.Call):
        if (not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS
                or node.keywords or len(node.args) != 1):
            raise ValueError("Only these one-argument functions are allowed: "
                             + ", ".join(FUNCTIONS) + ".")
        _validate(node.args[0], used, unknown)
    else:
        raise ValueError(SYNTAX_MESSAGE)


# ----------------------------------------------------------------------
# Numerical evaluation (NumPy)
# ----------------------------------------------------------------------

def _evaluate(node, values):
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id][0]
        return values[node.id]
    if isinstance(node, ast.UnaryOp):
        operand = _evaluate(node.operand, values)
        return -operand if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.Call):
        return FUNCTIONS[node.func.id][0](_evaluate(node.args[0], values))
    left = _evaluate(node.left, values)
    right = _evaluate(node.right, values)
    if isinstance(node.op, ast.Add):
        return left + right
    if isinstance(node.op, ast.Sub):
        return left - right
    if isinstance(node.op, ast.Mult):
        return left * right
    if isinstance(node.op, ast.Div):
        return np.divide(left, right)
    return np.power(left, right)


# ----------------------------------------------------------------------
# Symbolic version (SymPy), used only by the "Analysis" section
# ----------------------------------------------------------------------

def _to_sympy(node):
    if isinstance(node, ast.Constant):
        value = node.value
        return sp.Integer(value) if isinstance(value, int) else sp.Rational(repr(value))
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id][1]
        return SYMBOLS[node.id]
    if isinstance(node, ast.UnaryOp):
        operand = _to_sympy(node.operand)
        return -operand if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.Call):
        return FUNCTIONS[node.func.id][1](_to_sympy(node.args[0]))
    left, right = _to_sympy(node.left), _to_sympy(node.right)
    if isinstance(node.op, ast.Add):
        return left + right
    if isinstance(node.op, ast.Sub):
        return left - right
    if isinstance(node.op, ast.Mult):
        return left * right
    if isinstance(node.op, ast.Div):
        return left / right
    return _safe_power(left, right)


def _safe_power(base, exponent):
    """base ** exponent, refusing powers that would build enormous numbers."""
    if exponent.is_Number and abs(float(exponent)) > MAX_EXPONENT:
        raise ValueError(f"Exponents larger than {MAX_EXPONENT} are not supported.")
    if base.is_Number and exponent.is_Number:
        size = abs(float(base))
        if size not in (0.0, 1.0):
            bits = abs(float(exponent) * math.log2(size))
            if bits > MAX_POWER_BITS:
                raise ValueError("That power produces a number that is too large.")
    return base ** exponent
