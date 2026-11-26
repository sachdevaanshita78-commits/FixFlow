import joblib
import numpy as np

from pathlib import Path
from embedding_service import embedding_service


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "backend"
    / "priority_model.joblib"
)


class PriorityService:

    def __init__(self):

        # Load the saved model dictionary
        self.saved_data = joblib.load(MODEL_PATH)

        # Extract the trained classifier
        self.classifier = self.saved_data["members"][0]["clf"]

        print("Loaded model:", self.saved_data["winner"])

    def predict_priority(self, ticket_text):

        # Generate MPNet embedding
        embedding = embedding_service.generate_embeddings(
            [ticket_text]
        )

        # Predict priority
        prediction = self.classifier.predict(embedding)[0]

        # Get probabilities
        probabilities = self.classifier.predict_proba(embedding)[0]

        confidence = float(np.max(probabilities))

        return {
            "priority": str(prediction),
            "confidence": round(confidence, 4),
            "needs_review": (
                str(prediction) == "Critical"
                or confidence < self.saved_data["review_threshold"]
            )
        }


priority_service = PriorityService()
if __name__ == "__main__":

    tickets = [
        "Someone stole my debit card and made unauthorized transactions.",
        "Money was deducted but the receiver did not get it.",
        "My refund has been delayed for five days.",
        "How can I download my bank statement?"
    ]

    for ticket in tickets:
        print("\nProcessing:", ticket)
        result = priority_service.predict_priority(ticket)
        print("Result:", result)