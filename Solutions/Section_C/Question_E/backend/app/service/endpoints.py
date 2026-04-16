"""
endpoints.py

This module contains the main service functions for the CMS Facility Mortality Rates API endpoints.
It defines the logic for the summary, table, and analysis endpoints based on the filtered dataset.

Author: Xingyu Ji
"""

import pandas as pd
from typing import Optional
from service.filtering import filtering


def summary(
        df: pd.DataFrame,
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
) -> dict:
    """
    Generate summary statistics for facility mortality data based on filters.

    This endpoint returns overall metrics and top/bottom facilities after applying filters.

    Args:
        df (pd.DataFrame): Input dataset containing facility records.
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation (e.g., 'CA').
        zip_code (str, optional): 5-digit ZIP code.
        facility_name (str, optional): Partial facility name (case-insensitive match).

    Returns:
        dict: {
            "total": int,                  # total number of facilities after filtering
            "avgMortality": float | None, # average mortality rate
            "minMortality": float | None, # minimum mortality rate
            "maxMortality": float | None, # maximum mortality rate
            "top10Highest": list,         # top 10 facilities with highest mortality
            "top10Lowest": list           # top 10 facilities with lowest mortality
        }
    """
    # Apply filtering
    filtered_df = filtering(
        df=df,
        year=year,
        month=month,
        state=state,
        zip_code=zip_code,
        facility_name=facility_name,
    )

    # total = number of filtered facilities
    total = len(filtered_df)

    # Keep rows with valid mortality_rate for mortality stats
    valid_df = filtered_df.dropna(subset=["mortality_rate"]).copy()

    # If no valid mortality data exists after filtering
    if valid_df.empty:
        return {
            "total": total,
            "avgMortality": None,
            "minMortality": None,
            "maxMortality": None,
            "top10Highest": [],
            "top10Lowest": [],
        }

    # Calculate summary stats
    avg_mortality = round(valid_df["mortality_rate"].mean(), 4)
    min_mortality = round(valid_df["mortality_rate"].min(), 4)
    max_mortality = round(valid_df["mortality_rate"].max(), 4)

    # Get top 10 highest and lowest mortality facilities
    top10_highest = (
        valid_df.nlargest(10, "mortality_rate")[
            ["ccn", "facility_name", "state", "zip_code", "city", "mortality_rate"]
        ]
        .to_dict(orient="records")
    )

    top10_lowest = (
        valid_df.nsmallest(10, "mortality_rate")[
            ["ccn", "facility_name", "state", "zip_code", "city", "mortality_rate"]
        ]
        .to_dict(orient="records")
    )

    return {
        "total": total,
        "avgMortality": avg_mortality,
        "minMortality": min_mortality,
        "maxMortality": max_mortality,
        "top10Highest": top10_highest,
        "top10Lowest": top10_lowest,
    }


def table(
        df: pd.DataFrame,
        page: int = 1,
        pageSize: int = 20,
        sortBy: Optional[str] = None,
        sortOrder: str = "asc",
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
) -> dict:
    """
    Retrieve paginated facility data with optional filtering and sorting.

    This endpoint supports:
    - Filtering (year, month, state, zip_code, facility_name)
    - Sorting (multiple columns)
    - Pagination

    Args:
        df (pd.DataFrame): Input dataset containing facility records.
        page (int): Page number (starting from 1).
        pageSize (int): Number of records per page.
        sortBy (str, optional): Column name to sort by.
        sortOrder (str): Sorting order, either 'asc' or 'desc'.
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation.
        zip_code (str, optional): ZIP code.
        facility_name (str, optional): Partial facility name (case-insensitive).

    Returns:
        dict: {
            "data": list,     # paginated records
            "page": int,      # current page number
            "pageSize": int,  # page size
            "total": int      # total records after filtering
        }
    """
    # Validate pagination
    if page < 1:
        raise ValueError("page must be greater than or equal to 1")

    if pageSize < 1:
        raise ValueError("pageSize must be greater than or equal to 1")

    # Validate sorting
    allowed_sort_columns = {
        "ccn",
        "facility_name",
        "city",
        "state",
        "zip_code",
        "mortality_rate",
        "patient_count",
    }

    sortOrder = sortOrder.lower().strip()
    if sortOrder not in {"asc", "desc"}:
        raise ValueError("sortOrder must be either 'asc' or 'desc'")

    if sortBy is not None:
        sortBy = sortBy.strip()
        if sortBy and sortBy not in allowed_sort_columns:
            raise ValueError(
                f"sortBy must be one of: {sorted(allowed_sort_columns)}"
            )

    # Apply filtering
    filtered_df = filtering(
        df=df,
        year=year,
        month=month,
        state=state,
        zip_code=zip_code,
        facility_name=facility_name,
    )

    # Apply sorting
    if sortBy:
        ascending = sortOrder == "asc"

        # String columns: sort case-insensitively
        string_sort_columns = {
            "ccn",
            "facility_name",
            "city",
            "state",
            "zip_code",
        }

        if sortBy in string_sort_columns:
            page_df_source = filtered_df.assign(
                _sort_key=filtered_df[sortBy].astype(str).str.lower()
            ).sort_values(
                by="_sort_key",
                ascending=ascending,
                na_position="last",
            ).drop(columns="_sort_key")
            filtered_df = page_df_source
        else:
            filtered_df = filtered_df.sort_values(
                by=sortBy,
                ascending=ascending,
                na_position="last",
            )

    # Pagination
    total = len(filtered_df)
    start = (page - 1) * pageSize
    end = start + pageSize
    page_df = filtered_df.iloc[start:end].copy()

    return {
        "data": page_df.to_dict(orient="records"),
        "page": page,
        "pageSize": pageSize,
        "total": total,
    }


def analysis(
        df: pd.DataFrame,
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
) -> dict:
    """
    Generate aggregated analysis results based on filtered facility data.

    This endpoint performs data aggregation and returns:
    - Metrics grouped by state
    - Metrics grouped by ZIP code
    - Mortality rate distribution (bucketed ranges)
    - Monthly trend (currently not implemented)


    Args:
        df (pd.DataFrame): Input dataset containing facility records.
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation.
        zip_code (str, optional): ZIP code.
        facility_name (str, optional): Partial facility name (case-insensitive).

    Returns:
        dict: {
            "monthlyTrend": list,   # currently empty (not implemented)
            "byState": list,        # aggregated stats per state
            "byZip": list,          # aggregated stats per ZIP code
            "distribution": list    # mortality rate distribution buckets
        }

    Notes:
        - No monthly data is provided to calculate mortality trend.
        - Distribution is calculated using fixed bins (e.g., 0–10, 10–15, ..., 60+).
    """
    # Apply filtering
    filtered_df = filtering(
        df=df,
        year=year,
        month=month,
        state=state,
        zip_code=zip_code,
        facility_name=facility_name,
    )

    # Only rows with valid mortality_rate should be used for analysis metrics
    valid_df = filtered_df.dropna(subset=["mortality_rate"]).copy()

    # byState
    if valid_df.empty:
        return {
            "monthlyTrend": [],
            "byState": [],
            "byZip": [],
            "distribution": [],
        }
    else:
        by_state_df = (
            valid_df.groupby("state", dropna=False)
            .agg(
                facilityCount=("ccn", "count"),
                avgMortality=("mortality_rate", "mean"),
                minMortality=("mortality_rate", "min"),
                maxMortality=("mortality_rate", "max"),
            )
            .reset_index()
        )

        by_state_df["avgMortality"] = by_state_df["avgMortality"].round(4)
        by_state_df["minMortality"] = by_state_df["minMortality"].round(4)
        by_state_df["maxMortality"] = by_state_df["maxMortality"].round(4)

        by_state = by_state_df.to_dict(orient="records")

        # byZip
        by_zip_df = (
            valid_df.groupby("zip_code", dropna=False)
            .agg(
                facilityCount=("ccn", "count"),
                avgMortality=("mortality_rate", "mean"),
                minMortality=("mortality_rate", "min"),
                maxMortality=("mortality_rate", "max"),
            )
            .reset_index()
        )

        by_zip_df["avgMortality"] = by_zip_df["avgMortality"].round(4)
        by_zip_df["minMortality"] = by_zip_df["minMortality"].round(4)
        by_zip_df["maxMortality"] = by_zip_df["maxMortality"].round(4)

        by_zip = by_zip_df.to_dict(orient="records")

        # distribution
        bins = [0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, float("inf")]
        labels = [
            "0-10",
            "10-15",
            "15-20",
            "20-25",
            "25-30",
            "30-35",
            "35-40",
            "40-45",
            "45-50",
            "50-55",
            "55-60",
            "60+",
        ]

        distribution_df = valid_df.copy()
        distribution_df["range"] = pd.cut(
            distribution_df["mortality_rate"],
            bins=bins,
            labels=labels,
            right=False,
            include_lowest=True,
        )

        distribution_counts = (
            distribution_df["range"]
            .value_counts(sort=False, dropna=False)
            .reset_index()
        )
        distribution_counts.columns = ["range", "count"]

        distribution = [
            {
                "range": str(row["range"]),
                "count": int(row["count"]),
            }
            for _, row in distribution_counts.iterrows()
            if pd.notna(row["range"])
        ]

        monthly_trend = []

        return {
            "monthlyTrend": monthly_trend,
            "byState": by_state,
            "byZip": by_zip,
            "distribution": distribution,
        }
