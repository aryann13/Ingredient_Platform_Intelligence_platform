# Phase 1: Data Cleaning & Normalization (Cells 1 to 4)

This document contains the step-by-step interactive Pandas data cleaning code developed in `Phase1_Data_Cleaning.ipynb` up to **Cell 4**.

---

## Cell 1: Import Libraries & Configure File Paths

```python
import os
import pandas as pd
from pathlib import Path

# Define project data directory paths
DATA_DIR = Path("data")
INPUT_CSV = DATA_DIR / "multinational_brand_shortlist_sample.csv"  # Replace with multinational_brand_shortlist.csv when ready
OUTPUT_CSV = DATA_DIR / "multinational_brand_cleaned.csv"

print(f"Input CSV Path: {INPUT_CSV.resolve()}")
```

---

## Cell 2: Load the Raw Dataset & Inspect

```python
# Load raw CSV file into a Pandas DataFrame
df = pd.read_csv(INPUT_CSV)

print("=== Dataset Overview ===")
print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
df.head(10)
```

---

## Cell 3: Inspect Unique Brand Names to Spot Typos

```python
# Display unique brand names before cleaning
print("Raw Unique Brand Names:")
df['brand'].unique()
```

---

## Cell 4: Define Brand Replacement Rules & Cleaning Function

```python
# Brand typo dictionary mapping bad spelling -> correct brand name
typos = {
    "HERSHYEYS": "HERSHEYS",
    "BOUENVITA": "BOURNVITA",           # Preserved Bournvita as distinct beverage brand
    "CADBERY BORNVITA": "BOURNVITA",    # Standardized misspelling to Bournvita
    "MOUMTAIN DEW": "MOUNTAIN DEW",
    "DR OETKERS FUNFOODS": "DR OETKER",
    "NESTDLE": "NESTLE"
}

def fix_brand(name):
    # Skip empty or missing values safely
    if not isinstance(name, str):
        return name
    
    # Strip whitespace & standardize to uppercase
    clean_name = name.strip().upper()
    
    # Replace typo if found in dictionary
    if clean_name in typos:
        return typos[clean_name]
    
    # Return cleaned brand name
    return clean_name

# Quick verification test
print(fix_brand(" NESTDLE "))
print(fix_brand("BOUENVITA"))
```
