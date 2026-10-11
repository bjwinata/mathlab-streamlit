"""Lets the tests run even where Streamlit is not installed."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

try:
    import streamlit  # noqa: F401
except ImportError:
    sys.path.insert(0, HERE)
    import fake_streamlit
    fake_streamlit.install()
