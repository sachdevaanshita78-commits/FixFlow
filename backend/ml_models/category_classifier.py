
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "fixflow_category_model_clean.pkl"

model = joblib.load(MODEL_PATH)

CATEGORY_NAMES = {
    "BANKING": "Banking & Account Services",
    "CARDS": "Cards & Payments",
    "DIGITAL_BANKING": "Digital & Online Banking",
    "TRANSFERS": "Fund Transfers & Transactions",
    "LOANS": "Loans & Credit Services",
    "FRAUD": "Fraud & Disputes",
    "DEPOSITS": "Deposits & Investments",
    "COMPLIANCE": "KYC & Compliance",
    "TECHNICAL": "Technical Support",
    "ACCOUNT_ACCESS": "Account Access & Authentication",
    "BILLING": "Billing & Invoicing",
    "REFUNDS": "Refunds & Cancellations",
    "SERVICE_REQUEST": "General Service Requests",
    "PRODUCT": "Product & Service Information",
    "DOCUMENTATION": "Documents & Verification",
    "NETWORK": "Network & Connectivity",
    "HARDWARE": "Hardware & Device Support",
    "OTHER": "Other / Unclassified"
}


def predict_category(text: str):
    prediction = model.predict([text])[0]

    return {
        "category_id": prediction,
        "category_name": CATEGORY_NAMES[prediction]
    }
