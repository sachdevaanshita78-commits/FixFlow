
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score, classification_report


df = pd.read_csv("fixflow_category_train_clean.csv")

X = df["text"].astype(str)
y = df["category"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        max_features=50000,
        min_df=2,
        sublinear_tf=True
    )),
    ("classifier", LinearSVC(
        class_weight="balanced",
        C=1.0,
        random_state=42
    ))
])

print("Training category classifier...")

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, predictions))
print("Macro F1:", f1_score(y_test, predictions, average="macro"))
print("Weighted F1:", f1_score(y_test, predictions, average="weighted"))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

joblib.dump(model, "fixflow_category_model_clean.pkl")

print("\nClean category model saved successfully!")
