from typing import List, Optional
from pydantic import BaseModel


class PerformanceScenario(BaseModel):
    name: str
    description: Optional[str] = None
    return_pct: Optional[float] = None


class Costs(BaseModel):
    entry_cost_pct: Optional[float] = None
    ongoing_cost_pct: Optional[float] = None
    exit_cost_pct: Optional[float] = None


class PriipsFields(BaseModel):
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None
    isin: Optional[str] = None
    sri: Optional[int] = None
    recommended_holding_period: Optional[str] = None
    costs: Optional[Costs] = None
    performance_scenarios: Optional[List[PerformanceScenario]] = None
    date: Optional[str] = None
    language: Optional[str] = None
    source_url: Optional[str] = None


class ExtractRequest(BaseModel):
    sources: List[str]
    options: Optional[dict] = None


class ExtractResult(BaseModel):
    source: str
    success: bool
    data: Optional[PriipsFields] = None
    error: Optional[str] = None


