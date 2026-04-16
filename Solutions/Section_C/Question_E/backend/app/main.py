"""
main.py

This module defines the FastAPI application for the Dialysis Facility Mortality Analysis API.
It sets up the API endpoints for summary, table, and analysis based on the processed dataset.

Authors: Xingyu Ji
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import data_loader
from schemas import SummaryResponse, TableResponse, AnalysisResponse
from service.endpoints import summary, table, analysis

app = FastAPI(
    title="Dialysis Facility Mortality Analysis API",
    version="1.0.0"
)

allow_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once at startup
try:
    df = data_loader.load_data()
except Exception as e:
    raise RuntimeError(f"Failed to load processed data: {e}")


@app.get("/")
def root():
    """
    Health check endpoint.

    Returns:
        dict: Basic message indicating the API is running.
    """
    return {"message": "Dialysis Facility API is running"}


@app.get("/summary", response_model=SummaryResponse)
def get_summary(
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
):
    """
    Retrieve summary statistics for facility mortality data.

    This endpoint returns overall metrics and top/bottom facilities
    after applying optional filters.

    Query Parameters:
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation (e.g., 'CA').
        zip_code (str, optional): 5-digit ZIP code.
        facility_name (str, optional): Partial facility name (case-insensitive).

    Returns:
        SummaryResponse: Summary metrics including total count,
        mortality statistics, and top/bottom facilities.

    Raises:
        HTTPException (400): If input validation fails.
    """
    try:
        result = summary(
            df=df,
            year=year,
            month=month,
            state=state,
            zip_code=zip_code,
            facility_name=facility_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/table", response_model=TableResponse)
def get_table(
        page: int = 1,
        pageSize: int = 20,
        sortBy: Optional[str] = None,
        sortOrder: str = "asc",
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
):
    """
    Retrieve paginated facility data with optional filtering and sorting.

    This endpoint supports:
    - Filtering (year, month, state, zip_code, facility_name)
    - Sorting by selected columns
    - Pagination

    Query Parameters:
        page (int): Page number (starting from 1).
        pageSize (int): Number of records per page.
        sortBy (str, optional): Column name to sort by.
        sortOrder (str): 'asc' or 'desc'.
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation.
        zip_code (str, optional): ZIP code.
        facility_name (str, optional): Partial facility name.

    Returns:
        TableResponse: Paginated dataset including metadata.

    Raises:
        HTTPException (400): If input validation fails.
    """
    try:
        result = table(
            df=df,
            page=page,
            pageSize=pageSize,
            sortBy=sortBy,
            sortOrder=sortOrder,
            year=year,
            month=month,
            state=state,
            zip_code=zip_code,
            facility_name=facility_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analysis", response_model=AnalysisResponse)
def get_analysis(
        year: Optional[int] = None,
        month: Optional[int] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        facility_name: Optional[str] = None,
):
    """
    Retrieve aggregated analysis results for facility data.

    This endpoint performs aggregation (NOT pagination) and returns:
    - Metrics grouped by state
    - Metrics grouped by ZIP code
    - Mortality rate distribution

    Query Parameters:
        year (int, optional): Target year for filtering.
        month (int, optional): Target month (must be used with year).
        state (str, optional): State abbreviation.
        zip_code (str, optional): ZIP code.
        facility_name (str, optional): Partial facility name.

    Returns:
        AnalysisResponse: Aggregated analysis results.

    Raises:
        HTTPException (400): If input validation fails.
    """
    try:
        result = analysis(
            df=df,
            year=year,
            month=month,
            state=state,
            zip_code=zip_code,
            facility_name=facility_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
