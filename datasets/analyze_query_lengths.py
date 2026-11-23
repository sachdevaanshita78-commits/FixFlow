
import pandas as pd

files = {
    "BANKING77 Train": "banking77_train_decoded.csv",
    "BANKING77 Test": "banking77_test_decoded.csv",
    "IT Support Train": "it_support_train_decoded.csv",
    "IT Support Test": "it_support_test_decoded.csv"
}

for name, filename in files.items():
    df = pd.read_csv(filename)

    df["word_count"] = df["text"].fillna("").astype(str).str.split().str.len()

    print(f"\n{'=' * 50}")
    print(name)
    print(f"{'=' * 50}")

    print("Total queries:", len(df))
    print("Average words:", round(df["word_count"].mean(), 2))
    print("Minimum words:", df["word_count"].min())
    print("Maximum words:", df["word_count"].max())

    print("\nQuery length distribution:")
    print("1-5 words:", (df["word_count"] <= 5).sum())
    print("6-10 words:", ((df["word_count"] > 5) & (df["word_count"] <= 10)).sum())
    print("11-20 words:", ((df["word_count"] > 10) & (df["word_count"] <= 20)).sum())
    print("Above 20 words:", (df["word_count"] > 20).sum())

    print("\nExamples of short queries:")
    short_queries = df[df["word_count"] <= 5]["text"].head(10)

    for query in short_queries:
        print("-", query)
