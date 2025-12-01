# Supervised ML Explorer (Streamlit)

This folder contains a small Streamlit app to interactively explore supervised machine learning workflows.

How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-streamlit.txt
streamlit run app/streamlit_app.py
```

Default dataset: `files/cardio_train.csv` (binary `cardio` target) — you can also upload your own CSV.

Files added

- `app/streamlit_app.py` — main Streamlit UI
- `app/utils.py` — data loading and inference helpers
- `app/preprocessing.py` — preprocessing pipeline builder
- `app/models.py` — simple model wrappers and evaluation
- `app/visuals.py` — plotting helpers
- `app/save_load.py` — model export helpers
- `requirements-streamlit.txt` — dependencies for the app
