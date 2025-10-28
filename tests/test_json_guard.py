import pytest
from unittest.mock import patch

from app.utils.json_guard import try_parse_json


def test_try_parse_json_valid():
    """Test parsing valid JSON."""
    valid_json = '{"name": "test", "value": 123}'
    success, result = try_parse_json(valid_json)
    
    assert success is True
    assert result == {"name": "test", "value": 123}


def test_try_parse_json_invalid():
    """Test parsing invalid JSON."""
    invalid_json = '{"name": "test", "value": 123'  # Missing closing brace
    success, result = try_parse_json(invalid_json)
    
    assert success is False
    assert isinstance(result, str)  # Error message


def test_try_parse_json_with_markdown_fences():
    """Test parsing JSON wrapped in markdown code fences."""
    json_with_fences = '```\n{"name": "test"}\n```'
    success, result = try_parse_json(json_with_fences)
    
    assert success is True
    assert result == {"name": "test"}


def test_try_parse_json_with_markdown_fences_invalid():
    """Test parsing invalid JSON with markdown fences."""
    invalid_json_with_fences = '```json\n{"name": "test"\n```'  # Missing closing brace
    success, result = try_parse_json(invalid_json_with_fences)
    
    assert success is False
    assert isinstance(result, str)


def test_try_parse_json_empty_string():
    """Test parsing empty string."""
    success, result = try_parse_json("")
    
    assert success is False
    assert isinstance(result, str)


def test_try_parse_json_none():
    """Test parsing None input."""
    success, result = try_parse_json(None)
    
    assert success is False
    assert isinstance(result, str)
