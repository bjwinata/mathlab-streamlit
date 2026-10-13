"""A tiny stand-in for ``streamlit`` used for offline testing.

It records what a page would display and saves every figure to PNG, so the
page code can be executed (and the graphs inspected) without a Streamlit
server.  It is NOT used when the app runs for real.
"""

import os
import sys
import types


class _State(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class FakeStreamlit(types.ModuleType):
    def __init__(self, outdir="/tmp/mathlab_shots"):
        super().__init__("streamlit")
        self.outdir = outdir
        os.makedirs(outdir, exist_ok=True)
        self.session_state = _State()
        self.log = []          # (kind, content)
        self.figures = 0
        self.prefix = "page"
        self.clicked = set()   # keys of buttons to report as clicked

    # ---- helpers -----------------------------------------------------
    def _record(self, kind, content=""):
        self.log.append((kind, content))

    def reset(self, prefix):
        self.session_state.clear()
        self.log.clear()
        self.figures = 0
        self.prefix = prefix
        self.clicked = set()

    def texts(self, kind):
        return [c for k, c in self.log if k == kind]

    # ---- display -----------------------------------------------------
    def title(self, text, *a, **k): self._record("title", text)
    def subheader(self, text, *a, **k): self._record("subheader", text)
    def write(self, text="", *a, **k): self._record("write", text)
    def markdown(self, text="", *a, **k): self._record("markdown", text)
    def caption(self, text="", *a, **k): self._record("caption", text)
    def text(self, text="", *a, **k): self._record("text", text)
    def code(self, text="", *a, **k): self._record("code", text)
    def latex(self, text, *a, **k): self._record("latex", text)
    def info(self, text, *a, **k): self._record("info", text)
    def warning(self, text, *a, **k): self._record("warning", text)
    def error(self, text, *a, **k): self._record("error", text)
    def success(self, text, *a, **k): self._record("success", text)
    def metric(self, label, value, *a, **k): self._record("metric", (label, value))
    def set_page_config(self, *a, **k): pass
    def page_link(self, *a, **k): self._record("page_link", k.get("label", ""))
    def stop(self): raise SystemExit

    def pyplot(self, fig, *a, **k):
        self.figures += 1
        path = os.path.join(self.outdir, f"{self.prefix}_{self.figures}.png")
        fig.savefig(path, dpi=70)
        self._record("pyplot", path)

    # ---- widgets -----------------------------------------------------
    def _value(self, key, default):
        if key is not None:
            if key in self.session_state:
                return self.session_state[key]
            self.session_state[key] = default
        return default

    def number_input(self, label, min_value=None, max_value=None, value=0.0,
                     step=None, format=None, key=None, **k):
        return self._value(key, value)

    def slider(self, label, min_value=None, max_value=None, value=None,
               step=None, key=None, **k):
        return self._value(key, min_value if value is None else value)

    def selectbox(self, label, options, index=0, key=None, **k):
        return self._value(key, options[index])

    def radio(self, label, options, index=0, key=None, **k):
        return self._value(key, options[index])

    def checkbox(self, label, value=False, key=None, **k):
        return self._value(key, value)

    def button(self, label, key=None, on_click=None, args=(), **k):
        hit = (key or label) in self.clicked
        if hit and on_click:
            on_click(*args)
        return hit

    def text_input(self, label, value="", key=None, **k):
        return self._value(key, value)

    # ---- layout ------------------------------------------------------
    def columns(self, spec, *a, **k):
        n = spec if isinstance(spec, int) else len(spec)
        return [_Block(self) for _ in range(n)]

    def tabs(self, labels):
        return [_Block(self) for _ in labels]

    sidebar = property(lambda self: _Block(self))

    # ---- navigation --------------------------------------------------
    def Page(self, page, title=None, icon=None, url_path=None, default=False):
        return types.SimpleNamespace(page=page, title=title, icon=icon,
                                     url_path=url_path, default=default)

    def navigation(self, pages, **k):
        paths = [p.url_path for p in pages if p.url_path]
        assert len(paths) == len(set(paths)), "duplicate url_path"
        default = next(p for p in pages if p.default)
        self.pages = pages
        return types.SimpleNamespace(run=lambda: default.page())

    def container(self, *a, **k): return _Block(self)
    def expander(self, *a, **k): return _Block(self)


class _Block:
    """Works both as ``with block:`` and as ``block.some_widget(...)``."""

    def __init__(self, fake): self._fake = fake
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def __getattr__(self, name): return getattr(self._fake, name)


def install(outdir="/tmp/mathlab_shots"):
    fake = FakeStreamlit(outdir)
    sys.modules["streamlit"] = fake
    return fake
