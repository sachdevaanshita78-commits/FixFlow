import json
from pathlib import Path

import joblib


# Paths to the saved model and metadata
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "sentiment_artifacts"

MODEL_PATH = ARTIFACTS_DIR / "fixflow_banking_sentiment_model.joblib"
METADATA_PATH = ARTIFACTS_DIR / "fixflow_banking_sentiment_metadata.json"


# Load the model only when it is first needed
_model = None
_metadata = None


def load_sentiment_model():
    global _model, _metadata

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Sentiment model not found: {MODEL_PATH}"
            )

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                f"Sentiment metadata not found: {METADATA_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

        with open(METADATA_PATH, "r", encoding="utf-8") as file:
            _metadata = json.load(file)

    return _model, _metadata


def predict_sentiment(text: str) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Ticket text cannot be empty.")

    model, metadata = load_sentiment_model()

    prediction = model.predict([text])[0]

    return {
        "sentiment": str(prediction),
        "model_name": metadata["model_name"],
    }