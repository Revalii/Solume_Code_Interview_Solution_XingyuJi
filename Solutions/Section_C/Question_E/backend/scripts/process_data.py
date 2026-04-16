"""
process_data.py

This module handles the data processing for the CMS Facility Mortality Rates dataset.
It includes data used for the backend APIs.

Author: Xingyu Ji
"""

import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "DFC_FACILITY.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "cleaned.parquet"

REQUIRED_COLUMNS = {
    "CMS Certification Number (CCN)": "ccn",
    "Facility Name": "facility_name",
    "Address Line 1": "address_line_1",
    "City/Town": "city",
    "County/Parish": "county",
    "State": "state",
    "ZIP Code": "zip_code",
    "SMR Date": "smr_date",
    "Mortality Rate (Facility)": "mortality_rate",
    "Patient Survival data availability code": "mortality_availability_code",
    "Patient Survival Category Text": "mortality_category",
    "Number of Patients included in survival summary": "patient_count"
}

INVALID_NUMERIC_VALUES = {
    "",
    "Not Available",
    "N/A",
    "NA",
    "nan",
    "NaN",
    "--",
    "*",
}


# Load raw CSV data
def load_raw_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Raw file not found: {file_path}")

    return pd.read_csv(file_path, dtype=str, low_memory=False)


# Ensure all required columns exist
def validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns in raw dataset: " + ", ".join(missing)
        )


# Convert a raw value into a float if possible.
def parse_numeric(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if text in INVALID_NUMERIC_VALUES:
        return pd.NA

    text = text.replace(",", "")

    try:
        return float(text)
    except ValueError:
        return pd.NA


# Keep ZIP as a 5-digit string where possible.
def clean_zip(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    if text.isdigit():
        return text.zfill(5)

    return text


# Parse SMR_Date into separate year and month columns for start and end dates.
def parse_smr_date(value):
    if pd.isna(value):
        return pd.Series([pd.NA, pd.NA, pd.NA, pd.NA])

    text = str(value).strip()
    if not text:
        return pd.Series([pd.NA, pd.NA, pd.NA, pd.NA])

    match = re.match(r"^(\d{2}[A-Za-z]{3}\d{4})-(\d{2}[A-Za-z]{3}\d{4})$", text)
    if not match:
        return pd.Series([pd.NA, pd.NA, pd.NA, pd.NA])

    start_dt = pd.to_datetime(match.group(1), format="%d%b%Y", errors="coerce")
    end_dt = pd.to_datetime(match.group(2), format="%d%b%Y", errors="coerce")

    if pd.isna(start_dt) or pd.isna(end_dt):
        return pd.Series([pd.NA, pd.NA, pd.NA, pd.NA])

    return pd.Series([
        start_dt.year,
        start_dt.month,
        end_dt.year,
        end_dt.month,
    ])


# Process the raw dataframe: select and rename columns, clean data, parse dates, and handle missing values.
def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df[list(REQUIRED_COLUMNS.keys())].copy()
    df = df.rename(columns=REQUIRED_COLUMNS)

    for col in [
        "ccn",
        "facility_name",
        "address_line_1",
        "city",
        "county",
        "state",
        "zip_code",
        "smr_date",
        "mortality_availability_code",
        "mortality_category",
    ]:
        df[col] = df[col].astype("string").str.strip()

    df["zip_code"] = df["zip_code"].apply(clean_zip).astype("string")

    df["mortality_rate"] = pd.to_numeric(
        df["mortality_rate"].apply(parse_numeric),
        errors="coerce"
    )
    df["patient_count"] = pd.to_numeric(
        df["patient_count"].apply(parse_numeric),
        errors="coerce"
    )

    df[[
        "smr_start_year",
        "smr_start_month",
        "smr_end_year",
        "smr_end_month",
    ]] = df["smr_date"].apply(parse_smr_date)

    df["smr_start_year"] = pd.to_numeric(df["smr_start_year"], errors="coerce").astype("Int64")
    df["smr_start_month"] = pd.to_numeric(df["smr_start_month"], errors="coerce").astype("Int64")
    df["smr_end_year"] = pd.to_numeric(df["smr_end_year"], errors="coerce").astype("Int64")
    df["smr_end_month"] = pd.to_numeric(df["smr_end_month"], errors="coerce").astype("Int64")

    df["state"] = df["state"].str.upper()

    df = df.dropna(subset=["facility_name", "state", "zip_code"], how="any")
    df = df.dropna(subset=["smr_start_year", "smr_start_month", "smr_end_year", "smr_end_month"], how="any")

    df = df.reset_index(drop=True)
    return df


# Save cleaned dataframe to parquet.
def save_processed_data(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def print_summary(df: pd.DataFrame) -> None:
    print("\nCleaned Data Preview")
    print(df.head())

    print("\nColumns")
    print(df.columns.tolist())

    print("\nDtypes")
    print(df.dtypes)

    print("\nRow Count")
    print(len(df))

    print("\nMortality Rate Summary")
    print(df["mortality_rate"].describe())

    print("\nSMR Range Sample")
    print(
        df[[
            "smr_start_year",
            "smr_start_month",
            "smr_end_year",
            "smr_end_month",
        ]]
        .drop_duplicates()
        .sort_values([
            "smr_start_year",
            "smr_start_month",
            "smr_end_year",
            "smr_end_month",
        ])
        .head(20)
    )

    print("\nMissing Values")
    print(df.isna().sum())


if __name__ == "__main__":
    print(f"Loading raw file: {RAW_FILE}")
    df_raw = load_raw_data(RAW_FILE)

    print("Validating columns...")
    validate_columns(df_raw)

    print("Preparing dataframe...")
    df_clean = prepare_dataframe(df_raw)

    print(f"Saving cleaned data to: {OUTPUT_FILE}")
    save_processed_data(df_clean, OUTPUT_FILE)

    print_summary(df_clean)

    print("\nDone.")
