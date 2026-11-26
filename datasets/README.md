# FixFlow — Dataset Documentation

This directory contains the datasets, data preparation scripts, and supporting resources used in developing and training the machine learning components of **FixFlow**, an AI-powered customer support and issue-resolution platform.

The datasets primarily support automated ticket categorization by transforming customer support queries into structured, labeled training data.

---

## 1. Overview

FixFlow uses machine learning to understand incoming customer support tickets and automate important parts of the ticket-management workflow.

The category classification pipeline uses multiple data sources, including publicly available customer support datasets and manually curated examples, to build a domain-oriented training dataset.

The data preparation pipeline focuses on:

- Combining customer support datasets from different sources.
- Mapping original labels into FixFlow-specific categories.
- Cleaning and standardizing textual data.
- Incorporating manually curated examples.
- Preparing the final dataset for model training and evaluation.

## 2. Directory Structure

```text
datasets/
│
├── banking77_train.csv
├── bitext_mapped.csv
├── fixflow_category_train_clean.csv
├── fixflow_manual_examples.csv
│
├── build_clean_dataset.py
├── train_final_category_model.py
├── test_category_model.py
│
└── README.md
```

The trained category classification model is also maintained in:

```text
backend/ml_models/
    └── fixflow_category_model_clean.pkl
```

## 3. Dataset Sources

FixFlow uses a combination of publicly available datasets and custom-curated training examples.

### A. Banking77

**File:** `banking77_train.csv`

**Source:** [BANKING77 — PolyAI](https://github.com/PolyAI-LDN/task-specific-datasets)

BANKING77 is a banking-domain customer service dataset containing natural-language customer queries across 77 fine-grained banking intents.

**Purpose in FixFlow:**
- Provides banking-related customer queries.
- Adds domain-specific language and terminology.
- Helps improve the model's understanding of banking support requests.
- Provides examples that can be mapped to FixFlow's broader ticket categories.

**Original research:**  
*Clinc?* No — BANKING77 was introduced in the paper:

*Towards a Realistic Benchmark for Semi-Supervised Intent Classification*.

### B. Bitext Customer Support Dataset

**File:** `bitext_mapped.csv`

**Source:** [Bitext Customer Support Dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)

This dataset provides customer support queries and associated intent information across different support scenarios.

**Purpose in FixFlow:**
- Expands the diversity of customer support queries.
- Provides examples of different customer issues.
- Supports the development of broader issue-classification capabilities.
- Supplies additional examples for mapping into FixFlow categories.

### C. FixFlow Clean Training Dataset

**File:** `fixflow_category_train_clean.csv`

This is the final cleaned category-classification training dataset prepared for FixFlow.

It is derived from the selected source data and the project's preprocessing and label-mapping pipeline.

**Purpose:**
- Serves as the primary dataset for final category model training.
- Contains standardized customer support examples.
- Uses FixFlow-specific category labels.
- Provides a consistent representation of support requests across different domains.

### D. FixFlow Manual Examples

**File:** `fixflow_manual_examples.csv`

This dataset contains manually curated customer support examples created specifically for FixFlow.

**Purpose:**
- Adds project-specific customer support scenarios.
- Helps cover categories and situations that may not be adequately represented in public datasets.
- Improves the relevance of the training data to FixFlow's intended application.
- Supports the adaptation of generic customer support data to the FixFlow classification system.

---

## 4. Data Preprocessing Pipeline

The preprocessing pipeline converts heterogeneous customer support datasets into a standardized dataset suitable for machine learning.

The main stages include:

1. **Data collection:** Load the selected source datasets.
2. **Data inspection:** Examine the available text fields, labels, and dataset structure.
3. **Label mapping:** Map source-specific intents into FixFlow's classification categories.
4. **Text cleaning:** Prepare textual examples for consistent processing.
5. **Dataset integration:** Combine the selected data sources and manually curated examples.
6. **Data validation:** Check the resulting dataset for inconsistencies and invalid records.
7. **Final dataset generation:** Export the cleaned dataset used by the classification training pipeline.

### Preprocessing implementation

The main preprocessing script is:

```text
build_clean_dataset.py
```

This script is responsible for preparing the final category-classification dataset.

---

## 5. Model Training

The final cleaned dataset is used to train FixFlow's category classification model.

**Training script:**

```text
train_final_category_model.py
```

**Model artifact:**

```text
backend/ml_models/fixflow_category_model_clean.pkl
```

The trained model is integrated into the backend through:

```text
backend/ml_models/category_classifier.py
```

The backend uses this model to predict the category of incoming customer support tickets.

### Model testing

The testing script is:

```text
test_category_model.py
```

It is used to validate category-classification behavior using test examples.

For detailed model architecture, training configuration, and performance results, refer to the model training implementation and evaluation documentation.

---

## 6. How the Dataset Connects to FixFlow

The dataset pipeline supports the following workflow:

```text
Public Customer Support Datasets
              |
              v
       Data Preprocessing
              |
              v
        Label Mapping
              |
              v
     Manual Example Integration
              |
              v
   Final Clean Training Dataset
              |
              v
       Model Training
              |
              v
    Trained Category Model
              |
              v
       FixFlow Backend
              |
              v
  Automatic Ticket Classification
```

When a new support ticket is submitted, the backend processes its text and uses the trained classification model to predict an appropriate ticket category.

The predicted category can then be used by FixFlow's ticket-management and assignment workflows.

---

## 7. Reproducing the Training Pipeline

### Prerequisites

- Python 3.10 or later (use the Python version supported by the project's dependencies).
- Required Python packages from the root `requirements.txt`.
- The dataset files included in this directory.

### Step 1: Set up the environment

From the project root:

```bash
python -m venv venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Prepare the dataset

```bash
python datasets/build_clean_dataset.py
```

This runs the dataset preparation pipeline.

### Step 3: Train the category model

```bash
python datasets/train_final_category_model.py
```

### Step 4: Test the model

```bash
python datasets/test_category_model.py
```

**Note:** The scripts may use project-specific relative paths and training configurations. Run them from the project root and ensure their input and output paths match your local setup.

---

## 8. Dataset Licensing and Attribution

FixFlow uses external datasets alongside project-created examples.

Please retain the original dataset attribution and comply with the respective distribution and licensing requirements.

| Dataset | Attribution / Licence |
|---|---|
| BANKING77 | PolyAI — CC BY 4.0 |
| Bitext Customer Support Dataset | Bitext — CDLA-Sharing-1.0 (verify the exact upstream version and terms) |
| FixFlow Manual Examples | Project-created data |
| FixFlow Clean Dataset | Derived dataset; subject to the applicable upstream dataset terms |

### References

- [PolyAI BANKING77 Repository](https://github.com/PolyAI-LDN/task-specific-datasets)
- [BANKING77 Dataset on Hugging Face](https://huggingface.co/datasets/PolyAI/banking77)
- [Bitext Customer Support Dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)

Redistribution of derived datasets should respect the licences and attribution obligations of all included source material. Check the original licence files before redistributing the combined datasets.

---

## 9. Data Management Guidelines

To maintain a clean and reproducible project:

- Keep final training datasets separate from intermediate datasets.
- Preserve the original source attribution.
- Avoid committing duplicate or obsolete dataset versions.
- Exclude temporary files, caches, and unnecessary archives.
- Keep model artifacts separate from raw training data.
- Do not include personal, confidential, or sensitive customer information.
- Document changes to preprocessing and label-mapping logic.

Large datasets that exceed GitHub's normal file-size limits should be managed using Git LFS or an appropriate dataset-hosting platform.

---

## 10. Important Notes

- The datasets in this directory support the category-classification pipeline.
- Trained model artifacts are maintained separately in the backend.
- Training datasets are not required for ordinary model inference when the trained artifacts are already available.
- Reproducing training requires the appropriate source datasets, dependencies, and preprocessing scripts.
- Dataset labels and mappings should remain consistent with the categories supported by the FixFlow backend.

---

## 11. Project Information

**Project:** FixFlow  
**Domain:** AI-Powered Customer Support and Issue Resolution  
**Primary ML Task:** Automated Ticket Category Classification  
**Technology:** Python, Pandas, NumPy, Scikit-learn and other project dependencies.

**Repository:** [FixFlow on GitHub](https://github.com/sachdevaanshita78-commits/FixFlow)

---

*Maintained as part of the FixFlow project. This documentation describes the dataset organization and its role in the machine learning development pipeline.*