
import pandas as pd

# BANKING77
banking_train = pd.read_parquet("banking77_train.parquet")
banking_test = pd.read_parquet("banking77_test.parquet")

banking_train.to_csv("banking77_train.csv", index=False)
banking_test.to_csv("banking77_test.csv", index=False)

# IT SUPPORT TICKETS
it_train = pd.read_parquet("it_support_train.parquet")
it_test = pd.read_parquet("it_support_test.parquet")

it_train.to_csv("it_support_train.csv", index=False)
it_test.to_csv("it_support_test.csv", index=False)

# BITEXT is already in CSV format
bitext = pd.read_csv(
    "Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv"
)

print("All datasets processed successfully!")

print("\nBANKING77")
print("Train:", len(banking_train))
print("Test:", len(banking_test))

print("\nIT SUPPORT")
print("Train:", len(it_train))
print("Test:", len(it_test))

print("\nBITEXT")
print("Records:", len(bitext))

print("\nBitext columns:", bitext.columns.tolist())


# Inspect BANKING77
print("\n========== BANKING77 ==========")
print("Columns:", banking_train.columns.tolist())
print("\nSample records:")
print(banking_train.head(5).to_string())

print("\nOriginal categories:")
print(banking_train["label"].value_counts().head(20))

# Inspect IT SUPPORT
print("\n========== IT SUPPORT ==========")
print("Columns:", it_train.columns.tolist())
print("\nSample records:")
print(it_train.head(5).to_string())

# Inspect BITEXT
print("\n========== BITEXT ==========")
print("Sample records:")
print(bitext.head(5).to_string())

print("\nBitext categories:")
print(bitext["category"].value_counts())

print("\nBitext intents:")
print(bitext["intent"].value_counts())

print("\n========== BANKING77 LABELS ==========")
print(sorted(banking_train["label"].unique()))

print("\n========== IT SUPPORT LABELS ==========")
print(sorted(it_train["label"].unique()))


import pyarrow.parquet as pq
import json

files = {
    "BANKING77 TRAIN": "banking77_train.parquet",
    "IT SUPPORT TRAIN": "it_support_train.parquet"
}

for dataset_name, filename in files.items():
    print(f"\n========== {dataset_name} ==========")

    schema = pq.read_schema(filename)
    metadata = schema.metadata

    if metadata and b"huggingface" in metadata:
        hf_metadata = json.loads(metadata[b"huggingface"].decode("utf-8"))
        print(json.dumps(hf_metadata, indent=4))
    else:
        print("Hugging Face label metadata not found in this Parquet file.")

def get_label_names(filename):
    schema = pq.read_schema(filename)
    metadata = schema.metadata

    hf_metadata = json.loads(metadata[b"huggingface"].decode("utf-8"))

    return hf_metadata["info"]["features"]["label"]["names"]


# Get original label names from local Parquet files
banking_labels = get_label_names("banking77_train.parquet")
it_labels = get_label_names("it_support_train.parquet")


# Attach original names to BANKING77
banking_train["source_intent"] = banking_train["label"].map(
    dict(enumerate(banking_labels))
)

banking_test["source_intent"] = banking_test["label"].map(
    dict(enumerate(banking_labels))
)


# Attach original names to IT Support
it_train["source_category"] = it_train["label"].map(
    dict(enumerate(it_labels))
)

it_test["source_category"] = it_test["label"].map(
    dict(enumerate(it_labels))
)


# Save new files without modifying original CSV files
banking_train.to_csv("banking77_train_decoded.csv", index=False)
banking_test.to_csv("banking77_test_decoded.csv", index=False)

it_train.to_csv("it_support_train_decoded.csv", index=False)
it_test.to_csv("it_support_test_decoded.csv", index=False)


print("\n========== DECODED BANKING77 ==========")
print(banking_train[["text", "label", "source_intent"]].head(10))

print("\n========== DECODED IT SUPPORT ==========")
print(it_train[["text", "label", "source_category"]].head(10))

print("\nAll decoded files saved successfully!")
