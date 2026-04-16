"""
data_loader.py

This module provides a function to load the cleaned dialysis facility dataset from a parquet file for use in the backend API.

Author: Xingyu Ji
"""

from pathlib import Path
import pandas as pd
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "cleaned.parquet"


# Load the cleaned dataset from parquet and return it as a pandas DataFrame.
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {DATA_FILE}\n"
            "Please run scripts/process_data.py first."
        )

    df = pd.read_parquet(DATA_FILE)

    return df

# Uncomment this for prevents the file from read again for every request.
# @lru_cache(maxsize=1)
# def load_data() -> pd.DataFrame:
#     if not DATA_FILE.exists():
#         raise FileNotFoundError(
#             f"Processed data file not found: {DATA_FILE}\n"
#             "Please run scripts/process_data.py first."
#         )
#
#     return pd.read_parquet(DATA_FILE).copy()
