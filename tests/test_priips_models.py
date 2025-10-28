import pytest
from unittest.mock import patch

from app.models.priips import (
    PerformanceScenario, Costs, PriipsFields, 
    ExtractRequest, ExtractResult
)


def test_performance_scenario_model():
    """Test PerformanceScenario Pydantic model."""
    scenario = PerformanceScenario(
        name="Bull Market",
        description="Optimistic scenario",
        return_pct=15.5
    )
    
    assert scenario.name == "Bull Market"
    assert scenario.description == "Optimistic scenario"
    assert scenario.return_pct == 15.5


def test_performance_scenario_optional_fields():
    """Test PerformanceScenario with optional fields."""
    scenario = PerformanceScenario(name="Bear Market")
    
    assert scenario.name == "Bear Market"
    assert scenario.description is None
    assert scenario.return_pct is None


def test_costs_model():
    """Test Costs Pydantic model."""
    costs = Costs(
        entry_cost_pct=2.5,
        ongoing_cost_pct=1.2,
        exit_cost_pct=0.5
    )
    
    assert costs.entry_cost_pct == 2.5
    assert costs.ongoing_cost_pct == 1.2
    assert costs.exit_cost_pct == 0.5


def test_costs_optional_fields():
    """Test Costs with optional fields."""
    costs = Costs()
    
    assert costs.entry_cost_pct is None
    assert costs.ongoing_cost_pct is None
    assert costs.exit_cost_pct is None


def test_priips_fields_model():
    """Test PriipsFields Pydantic model."""
    performance_scenarios = [
        PerformanceScenario(name="Bull", return_pct=10.0),
        PerformanceScenario(name="Bear", return_pct=-5.0)
    ]
    costs = Costs(entry_cost_pct=1.0, ongoing_cost_pct=0.5)
    
    priips = PriipsFields(
        product_name="Test Fund",
        manufacturer="Test Company",
        isin="TEST123456789",
        sri=3,
        recommended_holding_period="5 years",
        costs=costs,
        performance_scenarios=performance_scenarios,
        date="2024-01-01",
        language="en",
        source_url="https://example.com/doc.pdf"
    )
    
    assert priips.product_name == "Test Fund"
    assert priips.manufacturer == "Test Company"
    assert priips.isin == "TEST123456789"
    assert priips.sri == 3
    assert priips.recommended_holding_period == "5 years"
    assert priips.costs == costs
    assert len(priips.performance_scenarios) == 2
    assert priips.date == "2024-01-01"
    assert priips.language == "en"
    assert priips.source_url == "https://example.com/doc.pdf"


def test_priips_fields_optional_fields():
    """Test PriipsFields with minimal required fields."""
    priips = PriipsFields()
    
    assert priips.product_name is None
    assert priips.manufacturer is None
    assert priips.isin is None
    assert priips.sri is None
    assert priips.recommended_holding_period is None
    assert priips.costs is None
    assert priips.performance_scenarios is None
    assert priips.date is None
    assert priips.language is None
    assert priips.source_url is None


def test_extract_request_model():
    """Test ExtractRequest Pydantic model."""
    request = ExtractRequest(
        sources=["https://example.com/doc1.pdf", "/path/to/doc2.pdf"],
        options={"language": "en", "ocr": False}
    )
    
    assert len(request.sources) == 2
    assert request.sources[0] == "https://example.com/doc1.pdf"
    assert request.sources[1] == "/path/to/doc2.pdf"
    assert request.options["language"] == "en"
    assert request.options["ocr"] is False


def test_extract_request_minimal():
    """Test ExtractRequest with minimal fields."""
    request = ExtractRequest(sources=["https://example.com/doc.pdf"])
    
    assert len(request.sources) == 1
    assert request.options is None


def test_extract_result_success():
    """Test ExtractResult for successful extraction."""
    priips_data = PriipsFields(product_name="Test Fund", isin="TEST123")
    result = ExtractResult(
        source="https://example.com/doc.pdf",
        success=True,
        data=priips_data
    )
    
    assert result.source == "https://example.com/doc.pdf"
    assert result.success is True
    assert result.data == priips_data
    assert result.error is None


def test_extract_result_failure():
    """Test ExtractResult for failed extraction."""
    result = ExtractResult(
        source="https://example.com/doc.pdf",
        success=False,
        error="Failed to parse PDF"
    )
    
    assert result.source == "https://example.com/doc.pdf"
    assert result.success is False
    assert result.error == "Failed to parse PDF"
    assert result.data is None


def test_model_validation():
    """Test Pydantic model validation."""
    # Test valid SRI values (1-7)
    for sri in range(1, 8):
        priips = PriipsFields(sri=sri)
        assert priips.sri == sri
    
    # Test that SRI can be None (optional field)
    priips = PriipsFields()
    assert priips.sri is None
