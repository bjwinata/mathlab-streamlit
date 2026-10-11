# Math Lab

Seven interactive mathematics projects in one web app, built with Streamlit.
© 2026 Jayden Winata

| Page | What it does |
|------|--------------|
| Project Parabola | Vertex, roots, focus, directrix, three equation forms and a live graph |
| Project Linear Inequality | Two linear inequalities, shaded overlap and intersection point |
| Project Compound Absolute Value | Two absolute-value inequalities combined with AND / OR |
| Project Compound Number Line | Two inequalities on aligned number lines, AND / OR |
| Project Completing the Square | Standard form to vertex form, step by step |
| Project Compound Interest | Five compounding methods, growth graph, full working |
| Project Logarithm | Transformations, inverses, base explorer, practice questions |

## Run it on your computer

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

It opens at <http://localhost:8501>.

## Put it online (free): Streamlit Community Cloud

1. Create a GitHub repository and upload everything in this folder
   (`app.py`, `requirements.txt`, `mathlab/`, `.streamlit/`).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **Create app**, pick the repository and branch, and set
   **Main file path** to `app.py`.
4. Click **Deploy**. After a minute or two you get a public link
   such as `https://your-app-name.streamlit.app`.

Any later `git push` to the repository redeploys the app automatically.
Other hosts that run Streamlit (Hugging Face Spaces, Render, Railway) work too:
the start command is `streamlit run app.py`.

## Project layout

```
app.py                  home page + navigation
requirements.txt
.streamlit/config.toml  theme
mathlab/
  formatting.py         number / LaTeX helpers shared by all pages
  parabola.py           one file per project: the maths at the top,
  linear_inequality.py  the Streamlit page (render()) at the bottom
  abs_inequality.py
  number_line.py
  completing_square.py
  compound_interest.py
  logarithm.py
tests/
  test_logic.py         checks of the maths   (python tests/test_logic.py)
  smoke_render.py       runs every page with a stand-in for Streamlit
```

To add a new project: create `mathlab/my_project.py` with a `render()` function,
then add one line to `PROJECTS` in `app.py`.
