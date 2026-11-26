import re
import joblib
import numpy as np
from pathlib import Path

from ml_models.embedding_service import embedding_service

MODEL_PATH = Path(__file__).resolve().parent / "priority_model.joblib"


class PriorityService:

    def __init__(self):
        d = joblib.load(MODEL_PATH)

        self.classes = list(d["classes"])
        self.minilm_name = d["encoders"]["minilm"]

        members = {m["name"]: m["clf"] for m in d["members"]}

        self.tfidf = members["tfidf"]
        self.minilm = members["minilm_C2"]

        for clf in (self.tfidf, self.minilm):
            assert list(clf.classes_) == self.classes, "class order mismatch"

        self.use_rule = d.get("use_rule", False)
        self.rules = [
            re.compile(p, re.IGNORECASE)
            for p in d.get("critical_patterns", [])
        ]

        print("Loaded ensemble:", d["winner"])

    def _rule_hit(self, text):
        return self.use_rule and any(
            r.search(text) for r in self.rules
        )

    def predict_priority(self, ticket_text):

        emb = embedding_service.generate_embeddings(
            [ticket_text],
            model_name=self.minilm_name
        )

        P = (
            self.tfidf.predict_proba([ticket_text])
            + self.minilm.predict_proba(emb)
        ) / 2

        probs = P[0]

        idx = int(np.argmax(probs))
        priority = self.classes[idx]
        confidence = float(probs[idx])

        rule_applied = False

        if priority != "Critical" and self._rule_hit(ticket_text):
            priority = "Critical"
            rule_applied = True
            confidence = float(
                probs[self.classes.index("Critical")]
            )

        return {
            "priority": priority,
            "confidence": round(confidence, 4),
            "probs": {
                c: round(float(p), 3)
                for c, p in zip(self.classes, probs)
            },
            "rule_applied": rule_applied
        }


priority_service = PriorityService()