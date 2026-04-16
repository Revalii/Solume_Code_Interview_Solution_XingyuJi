"""
filtering.py

This module contains the filtering logic for the CMS Facility Mortality Rates dataset.
It defines a function to apply various filters to the dataset based on user input.

Author: Xingyu Ji
"""

import pandas as pd
from typing import Optional


def filtering(
        df: pd.DataFrame,
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    This function applies the filtering logic to the dataset based on user input.

    Filter facility data by:
    - year
    - month (must be used with year)
    - state
    - zip_code
    - facility_name (case-insensitive partial match)

    Notes:
    - year/month filtering is based on whether the target period falls within:
      [smr_start_year, smr_start_month] to [smr_end_year, smr_end_month]
    - month cannot be used without year

    Args:
        df (pd.DataFrame): Input dataset containing facility records.
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (1–12). Must be used together with year.
        state (str, optional): State abbreviation (e.g., 'CA', 'NY').
        zip_code (str, optional): 5-digit ZIP code.
        facility_name (str, optional): Partial facility name for fuzzy matching (case-insensitive).

    Returns:
        pd.DataFrame: Filtered dataframe after applying all conditions, with index reset.
    """
    filtered_df = df.copy()

    # Validate inputs
    if month is not None and year is None:
        raise ValueError("month cannot be used without year")

    # Filter by state
    if state is not None:
        state = state.strip().upper()
        if state:
            filtered_df = filtered_df[
                filtered_df["state"].astype(str).str.upper() == state
                ]

    # Filter by ZIP code
    if zip_code is not None:
        zip_code = zip_code.strip()
        if zip_code:
            filtered_df = filtered_df[
                filtered_df["zip_code"].astype(str) == zip_code
                ]

    # Filter by facility name (contains, case-insensitive)
    if facility_name is not None:
        facility_name = facility_name.strip()
        if facility_name:
            filtered_df = filtered_df[
                filtered_df["facility_name"]
                .astype(str)
                .str.contains(facility_name, case=False, na=False)
            ]

    # Filter by year / month
    if year is not None:
        if month is not None:
            # Exact target month within SMR range
            target = year * 100 + month
            start = (
                    filtered_df["smr_start_year"].astype(int) * 100
                    + filtered_df["smr_start_month"].astype(int)
            )
            end = (
                    filtered_df["smr_end_year"].astype(int) * 100
                    + filtered_df["smr_end_month"].astype(int)
            )

            filtered_df = filtered_df[(start <= target) & (target <= end)]

        else:
            # Year overlap:
            # keep rows where the SMR range overlaps the requested year
            filtered_df = filtered_df[
                (filtered_df["smr_start_year"].astype(int) <= year)
                & (filtered_df["smr_end_year"].astype(int) >= year)
                ]

    return filtered_df.reset_index(drop=True)
