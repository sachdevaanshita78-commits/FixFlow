
import random
from itertools import product
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_DIR = Path(__file__).parent

OUTPUT_FILE = DATA_DIR / "fixflow_category_train_clean.csv"
CONFLICT_FILE = DATA_DIR / "fixflow_category_conflicts.csv"

BANKING77_FILE = DATA_DIR / "banking77_train.csv"
BITEXT_FILE = DATA_DIR / "bitext_mapped.csv"
MANUAL_FILE = DATA_DIR / "fixflow_manual_examples.csv"

RANDOM_SEED = 42
MAX_NETWORK_EXAMPLES = 500

random.seed(RANDOM_SEED)


# --------------------------------------------------
# BANKING77 LABEL MAPPING
# --------------------------------------------------

LABEL_TO_CATEGORY = {
    0: "CARDS",
    1: "PRODUCT",
    2: "CARDS",
    3: "HARDWARE",
    4: "TRANSFERS",
    5: "TRANSFERS",
    6: "DEPOSITS",
    7: "TRANSFERS",
    8: "TRANSFERS",
    9: "CARDS",
    10: "CARDS",
    11: "CARDS",
    12: "CARDS",
    13: "CARDS",
    14: "CARDS",
    15: "BILLING",
    16: "FRAUD",
    17: "CARDS",
    18: "HARDWARE",
    19: "BILLING",
    20: "FRAUD",
    21: "CARDS",
    22: "FRAUD",
    23: "CARDS",
    24: "PRODUCT",
    25: "CARDS",
    26: "CARDS",
    27: "TRANSFERS",
    28: "FRAUD",
    29: "CARDS",
    30: "BANKING",
    31: "BILLING",
    32: "PRODUCT",
    33: "DIGITAL_BANKING",
    34: "BILLING",
    35: "TRANSFERS",
    36: "PRODUCT",
    37: "CARDS",
    38: "CARDS",
    39: "CARDS",
    40: "CARDS",
    41: "FRAUD",
    42: "FRAUD",
    43: "CARDS",
    44: "DIGITAL_BANKING",
    45: "CARDS",
    46: "CARDS",
    47: "TRANSFERS",
    48: "TRANSFERS",
    49: "CARDS",
    50: "TRANSFERS",
    51: "REFUNDS",
    52: "REFUNDS",
    53: "REFUNDS",
    54: "PRODUCT",
    55: "BANKING",
    56: "BILLING",
    57: "BILLING",
    58: "DEPOSITS",
    59: "TRANSFERS",
    60: "TRANSFERS",
    61: "TRANSFERS",
    62: "CARDS",
    63: "FRAUD",
    64: "BILLING",
    65: "TRANSFERS",
    66: "TRANSFERS",
    67: "TRANSFERS",
    68: "COMPLIANCE",
    69: "COMPLIANCE",
    70: "COMPLIANCE",
    71: "COMPLIANCE",
    72: "CARDS",
    73: "PRODUCT",
    74: "COMPLIANCE",
    75: "HARDWARE",
    76: "BILLING"
}


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

all_records = []


def add_records(df, source):
    df = df[["text", "category"]].copy()

    df["text"] = df["text"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    df = df[
        (df["text"] != "") &
        (df["category"] != "") &
        (df["text"].str.lower() != "nan")
    ]

    df["source"] = source

    all_records.extend(
        df.to_dict(orient="records")
    )

    print(f"{source}: {len(df)} examples")


# --------------------------------------------------
# 1. BANKING77
# --------------------------------------------------

print("\nLoading Banking77...")

banking = pd.read_csv(BANKING77_FILE)

banking["category"] = banking["label"].map(
    LABEL_TO_CATEGORY
)

if banking["category"].isna().any():
    raise ValueError(
        "Banking77 contains unmapped labels."
    )

banking = banking[["text", "category"]]

add_records(banking, "banking77")


# --------------------------------------------------
# 2. CORRECTED BITEXT
# --------------------------------------------------

print("\nLoading corrected Bitext...")

bitext = pd.read_csv(BITEXT_FILE)

add_records(bitext, "bitext")


# --------------------------------------------------
# 3. MANUAL EXAMPLES
# --------------------------------------------------

print("\nLoading manual examples...")

manual = pd.read_csv(MANUAL_FILE)

add_records(manual, "manual")


# --------------------------------------------------
# 4. LOAN EXAMPLES
# --------------------------------------------------

print("\nGenerating loan examples...")

loan_products = [
    "personal loan",
    "home loan",
    "education loan",
    "car loan",
    "business loan",
    "vehicle loan",
    "property loan",
    "student loan"
]

amounts = [
    "2 lakh",
    "5 lakh",
    "8 lakh",
    "10 lakh",
    "15 lakh",
    "20 lakh"
]

loan_templates = [
    "I want to apply for a {product}.",
    "How can I submit an application for a {product}?",
    "Am I eligible for a {product} of {amount}?",
    "What are the eligibility requirements for a {product}?",
    "What is the current status of my {product} application?",
    "My {product} application is still pending. Please help.",
    "My approved {product} amount has not been credited yet.",
    "When will my {product} amount be disbursed?",
    "I need help understanding my {product} EMI.",
    "My monthly EMI amount seems incorrect.",
    "How can I repay my outstanding {product} amount?",
    "I want to make an early repayment on my {product}.",
    "What interest rate applies to my {product}?",
    "Why has the interest rate on my loan increased?",
    "I want to close my {product} before its maturity date.",
    "What is the foreclosure process for my {product}?",
    "My {product} application was rejected. Why?",
    "Please explain the reason for my loan rejection.",
    "I have repaid my {product} and need a closure certificate.",
    "Please provide a no-dues certificate for my loan.",
    "My {product} EMI is overdue. What should I do?",
    "Please explain the overdue charges on my {product}.",
    "What documents are required for a {product}?",
    "My loan application document verification is pending.",
    "Can I get a top-up on my existing {product}?",
    "I want to increase the amount of my current loan."
]

loan_rows = []

for template, product_name, amount in product(
    loan_templates,
    loan_products,
    amounts
):
    loan_rows.append({
        "text": template.format(
            product=product_name,
            amount=amount
        ),
        "category": "LOANS"
    })

loan_df = pd.DataFrame(loan_rows).drop_duplicates(
    subset=["text"]
)

add_records(loan_df, "synthetic_loans")


# --------------------------------------------------
# 5. NETWORK EXAMPLES
# --------------------------------------------------

print("\nGenerating network examples...")

network_templates = [
    "I cannot connect to the {network} network.",
    "The {network} connection keeps disconnecting.",
    "I am experiencing slow {network} connectivity.",
    "The {network} service is unavailable.",
    "My device cannot detect the {network} network.",
    "The {network} connection keeps timing out.",
    "I am unable to access services because of a {network} outage.",
    "The {network} connection drops whenever I try to use the service.",
    "Please investigate the unstable {network} connection.",
    "I keep receiving a network connection error.",
    "The application cannot reach the server because of a network issue.",
    "My connection becomes unavailable after a few minutes.",
    "I am facing intermittent connectivity problems.",
    "The network is connected but no data is loading.",
    "Please help resolve the recurring connectivity failure.",
    "The service is unreachable from my current network.",
    "I am getting a connection timeout while accessing the platform.",
    "The network keeps showing limited connectivity.",
    "I cannot access the service due to an internet outage.",
    "The connection is too unstable to complete my request."
]

network_types = [
    "Wi-Fi",
    "mobile",
    "office",
    "home",
    "internet",
    "VPN",
    "wireless",
    "broadband",
    "corporate",
    "local"
]

network_contexts = [
    "while accessing the customer portal",
    "when using the application",
    "during online transactions",
    "after logging into the platform",
    "while connecting to the server",
    "during business hours",
    "after restarting my device",
    "when accessing online services",
    "from multiple devices",
    "even though other websites are working"
]

network_combinations = list(
    product(
        network_templates,
        network_types,
        network_contexts
    )
)

network_combinations = random.sample(
    network_combinations,
    min(
        MAX_NETWORK_EXAMPLES,
        len(network_combinations)
    )
)

network_rows = []

for template, network, context in network_combinations:
    network_rows.append({
        "text": (
            template.format(network=network)
            + " "
            + context
            + "."
        ),
        "category": "NETWORK"
    })

network_df = pd.DataFrame(network_rows).drop_duplicates(
    subset=["text"]
)

add_records(network_df, "synthetic_network")


# --------------------------------------------------
# 6. DOCUMENTATION EXAMPLES
# --------------------------------------------------

print("\nGenerating documentation examples...")

documentation_templates = [
    "I cannot upload the {document} required for my application.",
    "The system is rejecting my {document}.",
    "My uploaded {document} is not appearing in the portal.",
    "Please tell me how to submit the {document}.",
    "The {document} upload keeps failing.",
    "I need to replace an incorrect {document}.",
    "The portal says my {document} is missing.",
    "I uploaded the {document} but it is still showing as pending.",
    "What file format is accepted for the {document}?",
    "The uploaded {document} is not readable.",
    "I am unable to attach the {document} to my request.",
    "Please help me correct the {document} submission.",
    "The document upload page is not accepting my file.",
    "I need a copy of the document submitted with my request.",
    "My application is waiting for a required document.",
    "The system shows an error when I submit the {document}.",
    "How can I download the document associated with my request?",
    "I accidentally uploaded the wrong {document}.",
    "The portal is not saving my uploaded document.",
    "Please confirm whether my {document} was received."
]

documents = [
    "supporting document",
    "application form",
    "service agreement",
    "proof of address",
    "proof of purchase",
    "signed form",
    "authorization letter",
    "invoice copy",
    "identity document",
    "account statement"
]

documentation_rows = []

for template, document in product(
    documentation_templates,
    documents
):
    documentation_rows.append({
        "text": template.format(document=document),
        "category": "DOCUMENTATION"
    })

documentation_df = pd.DataFrame(
    documentation_rows
).drop_duplicates(subset=["text"])

add_records(
    documentation_df,
    "synthetic_documentation"
)


# --------------------------------------------------
# 7. REMAINING CATEGORIES
# --------------------------------------------------

print("\nGenerating remaining category examples...")

remaining_templates = {

    "TECHNICAL": [
        "The application crashes whenever I try to {action}.",
        "I am getting an unexpected error while trying to {action}.",
        "The system is not responding when I attempt to {action}.",
        "Please fix the software issue preventing me from {action}.",
        "The platform freezes whenever I try to {action}.",
        "I keep receiving an error message while trying to {action}.",
        "The feature stopped working after the latest update.",
        "The application is behaving unexpectedly when I {action}.",
        "I cannot complete the process because the system keeps failing.",
        "The page displays a technical error whenever I {action}.",
        "The application closes unexpectedly during the process.",
        "Please investigate the recurring software malfunction.",
        "The system is showing a blank screen when I open the feature.",
        "My request fails because of an internal application error.",
        "The platform is not processing my request correctly.",
        "The application becomes unresponsive after I submit the form.",
        "I am unable to use this feature due to a software bug.",
        "The system keeps displaying an unexpected exception.",
        "The latest update appears to have broken this feature.",
        "Please help resolve this recurring application malfunction."
    ],

    "DIGITAL_BANKING": [
        "I cannot log in to my mobile banking application.",
        "My internet banking session keeps expiring.",
        "The banking app is not opening on my phone.",
        "I cannot access my account through online banking.",
        "Mobile banking is showing an unexpected error.",
        "My banking application is not loading account details.",
        "I am unable to register for mobile banking.",
        "The internet banking website is not working.",
        "I cannot activate mobile banking on my device.",
        "My banking app keeps logging me out.",
        "The online banking dashboard is not displaying correctly.",
        "I cannot access the mobile banking services.",
        "My banking app is stuck on the loading screen.",
        "Please help me activate internet banking.",
        "The mobile banking application is not synchronizing.",
        "I am unable to use the bank's digital services.",
        "My online banking access has stopped working.",
        "The banking app is not recognizing my registered device.",
        "I cannot complete a banking request through the app.",
        "The digital banking portal keeps showing an error."
    ],

    "BANKING": [
        "I want to open a new bank account.",
        "How can I close my existing savings account?",
        "Please provide my bank account statement.",
        "I need to update my bank account details.",
        "How can I change the nominee on my account?",
        "I want to convert my savings account into a different account type.",
        "Please explain the minimum balance requirement.",
        "I need information about the services linked to my account.",
        "How can I update my registered address in the bank?",
        "I want to request a new account statement.",
        "Please tell me the process for closing my account.",
        "I need to update my personal details in my bank account.",
        "Can you explain the features of my savings account?",
        "I want to know the current status of my account.",
        "How can I add a nominee to my bank account?",
        "I need assistance with maintaining my bank account.",
        "Please provide details about my account type.",
        "I want to change my bank account's communication address.",
        "How do I request an account balance certificate?",
        "I need help with general bank account services."
    ],

    "DEPOSITS": [
        "What is the current interest rate on a fixed deposit?",
        "I want to open a recurring deposit account.",
        "When will my fixed deposit mature?",
        "How can I withdraw my fixed deposit before maturity?",
        "Please provide the maturity amount of my deposit.",
        "I want to renew my fixed deposit.",
        "How is interest calculated on my recurring deposit?",
        "Can I change the tenure of my fixed deposit?",
        "My deposit interest has not been credited.",
        "I need a statement for my fixed deposit.",
        "What are the premature withdrawal rules for an FD?",
        "I want to close my recurring deposit.",
        "Please explain the tax implications of my fixed deposit.",
        "My fixed deposit maturity amount appears incorrect.",
        "Can I get a loan against my fixed deposit?",
        "I want to reinvest my matured deposit.",
        "Please tell me the current deposit rates.",
        "My recurring deposit installment was not recorded.",
        "How can I change the nominee on my fixed deposit?",
        "I need help with my bank deposit investment."
    ],

    "HARDWARE": [
        "The ATM screen is not responding.",
        "The cash dispenser is not releasing money.",
        "The ATM is unable to read my card.",
        "The receipt printer at the ATM is not working.",
        "The POS terminal keeps restarting.",
        "The card reader at the payment terminal is damaged.",
        "The ATM touchscreen is not functioning properly.",
        "The cash deposit machine is out of order.",
        "The payment terminal is not powering on.",
        "The ATM keypad buttons are not working.",
        "The POS device is displaying a hardware error.",
        "The ATM printer is producing blank receipts.",
        "The card insertion slot appears to be jammed.",
        "The branch token display machine is not working.",
        "The biometric scanner is not detecting fingerprints.",
        "The payment terminal screen is physically damaged.",
        "The ATM is making unusual mechanical noises.",
        "The cash counting machine is malfunctioning.",
        "The bank kiosk is not responding to touch.",
        "Please arrange repair of the faulty ATM equipment."
    ]
}

actions = [
    "submit a request",
    "download a report",
    "save my changes",
    "open the dashboard",
    "complete a form",
    "generate a document",
    "access a feature",
    "process information",
    "update my details",
    "view my records",
    "submit information",
    "retrieve my data",
    "complete the operation",
    "load the required page",
    "continue to the next step"
]

remaining_rows = []

for category, templates in remaining_templates.items():
    for template in templates:
        if "{action}" in template:
            for action in actions:
                remaining_rows.append({
                    "text": template.format(action=action),
                    "category": category
                })
        else:
            remaining_rows.append({
                "text": template,
                "category": category
            })

remaining_df = pd.DataFrame(
    remaining_rows
).drop_duplicates(subset=["text"])

add_records(
    remaining_df,
    "synthetic_remaining"
)


# --------------------------------------------------
# 8. COMBINE AND CHECK LABEL CONFLICTS
# --------------------------------------------------

print("\nCombining all sources...")

combined = pd.DataFrame(all_records)

combined["text"] = combined["text"].str.strip()
combined["category"] = combined["category"].str.strip()

# Remove exact duplicate text/category/source records
combined = combined.drop_duplicates(
    subset=["text", "category", "source"]
)

# Find texts assigned to multiple categories
category_counts = combined.groupby("text")[
    "category"
].nunique()

conflicting_texts = category_counts[
    category_counts > 1
].index

conflicts = combined[
    combined["text"].isin(conflicting_texts)
].sort_values("text")

conflicts.to_csv(
    CONFLICT_FILE,
    index=False
)

# Exclude ambiguous cross-category duplicate texts
clean = combined[
    ~combined["text"].isin(conflicting_texts)
].copy()

# Merge provenance when the same text/category occurs in multiple sources
clean = (
    clean.groupby(
        ["text", "category"],
        as_index=False
    )
    .agg({
        "source": lambda values: "|".join(
            sorted(set(values))
        )
    })
)

clean = clean.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)


# --------------------------------------------------
# 9. FINAL VALIDATION
# --------------------------------------------------

if clean.empty:
    raise ValueError("The final dataset is empty.")

if clean["text"].isna().any():
    raise ValueError("Missing text values found.")

if clean["category"].isna().any():
    raise ValueError("Missing category values found.")

if clean["text"].duplicated().any():
    raise ValueError("Duplicate text values found.")

clean.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# 10. SUMMARY
# --------------------------------------------------

print("\n======================================")
print("CLEAN DATASET CREATED SUCCESSFULLY")
print("======================================")

print("\nFinal records:", len(clean))
print("Conflicting examples excluded:", len(conflicts))
print("Unique categories:", clean["category"].nunique())

print("\nCategory distribution:")
print(
    clean["category"].value_counts().to_string()
)

print("\nSource distribution:")
print(
    clean["source"].value_counts().to_string()
)

print("\nSaved dataset:", OUTPUT_FILE)
print("Saved conflicts:", CONFLICT_FILE)
