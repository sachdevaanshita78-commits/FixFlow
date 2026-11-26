
import joblib

model = joblib.load("fixflow_category_model_clean.pkl")

test_messages = [
    "My UPI transaction failed but money was deducted.",
    "Someone made an unauthorized withdrawal from my account.",
    "I want to apply for a personal loan.",
    "My debit card is not working at the ATM.",
    "I cannot log in to my banking application.",
    "I want to know the interest rate on a fixed deposit.",
    "My KYC verification was rejected.",
    "I need a copy of my bank statement.",
    "The bank charged me an unexpected maintenance fee.",
    "I want to speak to a customer support representative."
]

predictions = model.predict(test_messages)

for message, category in zip(test_messages, predictions):
    print(f"\nMessage: {message}")
    print(f"Predicted category: {category}")
