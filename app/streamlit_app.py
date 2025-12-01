import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline

from app.utils import list_workspace_csvs, load_csv, preview_dataframe, infer_target_column
from app.preprocessing import build_preprocessor
from app.models import get_model, train_and_evaluate
from app.visuals import plot_confusion_matrix, plot_roc, plot_precision_recall
from app.save_load import save_model_to_bytes
import io


st.set_page_config(page_title="Supervised ML Explorer", layout="wide")


def main():
    st.title("Supervised ML Explorer — Interactive Demo")

    # Sidebar: dataset selection
    st.sidebar.header("Data")
    datasets = list_workspace_csvs(".")
    choice = st.sidebar.selectbox("Choose demo dataset", ["-- upload or choose --"] + datasets)
    uploaded = st.sidebar.file_uploader("Or upload a CSV", type=["csv"])

    df = None
    if uploaded is not None:
        df = load_csv(uploaded)
    elif choice and choice != "-- upload or choose --":
        df = load_csv(choice)

    if df is None:
        st.info("Please select a dataset from the sidebar or upload a CSV.")
        return

    st.subheader("Data preview")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    st.dataframe(preview_dataframe(df, 10))

    # Target and features
    st.sidebar.header("Model")
    inferred = infer_target_column(df)
    target = st.sidebar.selectbox("Target column", ["(none)"] + list(df.columns), index=(1 if inferred else 0))
    if target == "(none)":
        st.warning("Select a target column to continue")
        return

    feature_cols = [c for c in df.columns if c != target]
    selected_features = st.sidebar.multiselect("Features", feature_cols, default=feature_cols)

    # Data split and preprocessing
    test_size = st.sidebar.slider("Test set proportion", 0.05, 0.5, 0.2)
    random_state = st.sidebar.number_input("Random seed", value=42)
    scaler = st.sidebar.selectbox("Scaler", ["standard", "robust", "minmax"])
    impute = st.sidebar.selectbox("Impute strategy", ["mean", "median", "most_frequent"]) 

    # Model selection
    model_name = st.sidebar.selectbox("Model", ["LogisticRegression", "RandomForest"])
    if model_name == "RandomForest":
        n_estimators = st.sidebar.slider("n_estimators", 10, 500, 100)
        max_depth = st.sidebar.slider("max_depth (None=0)", 0, 50, 0)
        rf_params = {"n_estimators": n_estimators}
        if max_depth > 0:
            rf_params["max_depth"] = max_depth
        model_params = rf_params
    else:
        C = st.sidebar.number_input("C (inverse reg strength)", value=1.0, format="%f")
        model_params = {"C": float(C)}

    # Train button
    if st.sidebar.button("Train model"):
        X = df[selected_features].copy()
        y = df[target].copy()

        # Detect numeric / categorical
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [c for c in selected_features if c not in numeric_cols]

        preproc = build_preprocessor(numeric_cols, categorical_cols, scaler=scaler, impute_strategy=impute)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=int(random_state))

        base_model = get_model(model_name, model_params)
        # pipeline: preprocessor then model
        from sklearn.pipeline import Pipeline

        pipeline = Pipeline([
            ("preproc", preproc),
            ("model", base_model),
        ])

        with st.spinner("Training..."):
            fitted_model, metrics = train_and_evaluate(pipeline, X_train, X_test, y_train, y_test)

        st.success("Training complete")
        st.subheader("Metrics")
        st.json(metrics)

        # Predictions for visuals
        try:
            y_pred = fitted_model.predict(X_test)
            y_proba = None
            try:
                y_proba = fitted_model.predict_proba(X_test)[:, 1]
            except Exception:
                y_proba = None

            st.subheader("Plots")
            st.pyplot(plot_confusion_matrix(y_test, y_pred))
            if y_proba is not None:
                st.pyplot(plot_roc(y_test, y_proba))
                st.pyplot(plot_precision_recall(y_test, y_proba))
        except Exception as e:
            st.warning(f"Could not create plots: {e}")

        # Download model
        try:
            bytes_obj = save_model_to_bytes(fitted_model)
            st.download_button("Download trained model (.joblib)", data=bytes_obj, file_name="model.joblib")
        except Exception as e:
            st.warning(f"Could not prepare model download: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("Built from course examples — supports binary classification demos.")


if __name__ == "__main__":
    main()
