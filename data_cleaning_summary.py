#!/usr/bin/env python3
"""
clean_data.py

Data cleaning and preprocessing script.
Usage:
    python clean_data.py --input data/raw/raw_data.csv --output data/clean/clean_data.csv
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# ------------------------------------------------------
# Utility Functions
# ------------------------------------------------------

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    print(f"✅ Removed {before - len(df)} duplicate rows.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values by imputing or dropping."""
    # Example: Fill numeric columns with median, categorical with mode
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(exclude=np.number).columns

    for col in num_cols:
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)

    for col in cat_cols:
        mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
        df[col].fillna(mode_val, inplace=True)

    print("✅ Missing values handled (numeric→median, categorical→mode).")
    return df


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace and standardize text to title case."""
    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
    print("✅ Text columns standardized (trimmed + title case).")
    return df


def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert any column containing 'date' in its name to datetime format."""
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
    print("✅ Date columns converted to datetime where possible.")
    return df


def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Clip outliers using the IQR method for numeric columns."""
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        df[col] = df[col].clip(lower, upper)
    print("✅ Outliers clipped using IQR method.")
    return df


def validate_data(df: pd.DataFrame) -> None:
    """Basic validation checks."""
    print("\n--- Data Validation ---")
    print(df.info())
    print("\nNull Values After Cleaning:\n", df.isnull().sum())
    print("-------------------------")


# ------------------------------------------------------
# Main Cleaning Workflow
# ------------------------------------------------------

def clean_data(input_path: Path, output_path: Path) -> None:
    """Full cleaning pipeline."""
    print(f"📂 Loading dataset: {input_path}")
    df = pd.read_csv(input_path)

    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = standardize_text(df)
    df = standardize_dates(df)
    df = handle_outliers(df)

    validate_data(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n💾 Cleaned dataset saved to: {output_path}")


# ------------------------------------------------------
# CLI
# ------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and preprocess raw dataset.")
    parser.add_argument("--input", required=True, help="Path to input raw CSV file.")
    parser.add_argument("--output", required=True, help="Path to save cleaned CSV file.")
    args = parser.parse_args()

    clean_data(Path(args.input), Path(args.output))
