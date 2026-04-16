"""
schemas.py

This module defines the Pydantic models for request validation and response formatting for the CMS Facility Mortality Rates API.

Author: Xingyu Ji
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator


# Input Schemas
class FilterParams(BaseModel):
    year: Optional[int] = Field(default=None, ge=2021, le=2024)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    state: Optional[str] = None
    zip_code: Optional[str] = None
    facility_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_month_with_year(self):
        if self.month is not None and self.year is None:
            raise ValueError("month cannot be used without year")
        return self


class TableParams(FilterParams):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1)
    sortBy: Optional[str] = None
    sortOrder: Literal["asc", "desc"] = "asc"


# Shared Output Schemas
class FacilityRecord(BaseModel):
    ccn: str
    facility_name: str
    address_line_1: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: str
    zip_code: str
    smr_date: str
    mortality_rate: Optional[float] = None
    mortality_availability_code: Optional[str] = None
    mortality_category: Optional[str] = None
    patient_count: Optional[float] = None
    smr_start_year: int
    smr_start_month: int
    smr_end_year: int
    smr_end_month: int


class SummaryRankItem(BaseModel):
    ccn: str
    facility_name: str
    state: str
    zip_code: str
    city: Optional[str] = None
    mortality_rate: float


# Summary Response
class SummaryResponse(BaseModel):
    total: int
    avgMortality: Optional[float] = None
    minMortality: Optional[float] = None
    maxMortality: Optional[float] = None
    top10Highest: List[SummaryRankItem]
    top10Lowest: List[SummaryRankItem]


# Table Response
class TableResponse(BaseModel):
    data: List[FacilityRecord]
    page: int
    pageSize: int
    total: int


# Analysis Response
class ByStateItem(BaseModel):
    state: str
    facilityCount: int
    avgMortality: Optional[float] = None
    minMortality: Optional[float] = None
    maxMortality: Optional[float] = None


class ByZipItem(BaseModel):
    zip_code: str
    facilityCount: int
    avgMortality: Optional[float] = None
    minMortality: Optional[float] = None
    maxMortality: Optional[float] = None


class DistributionItem(BaseModel):
    range: str
    count: int


class MonthlyTrendItem(BaseModel):
    period: str
    avgMortality: Optional[float] = None
    facilityCount: int = 0


class AnalysisResponse(BaseModel):
    monthlyTrend: List[MonthlyTrendItem]
    byState: List[ByStateItem]
    byZip: List[ByZipItem]
    distribution: List[DistributionItem]
