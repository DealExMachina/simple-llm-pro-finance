import pytest
from unittest.mock import AsyncMock, patch

from app.services.extract_service import build_prompt, process_source, extract
from app.models.priips import ExtractRequest, ExtractResult, PriipsFields


def test_build_prompt():
    """Test prompt building with schema instructions."""
    text = "Test document content"
    prompt = build_prompt(text)
    
    assert "expert financial document parser" in prompt
    assert "STRICT JSON only" in prompt
    assert "product_name" in prompt
    assert "manufacturer" in prompt
    assert "isin" in prompt
    assert "sri" in prompt
    assert "Test document content" in prompt


def test_build_prompt_long_text():
    """Test prompt building with very long text (should be truncated)."""
    long_text = "x" * 20000
    prompt = build_prompt(long_text)
    
    # Should be truncated to 15000 chars
    assert len(prompt) < 20000
    assert "Document:\n" in prompt


@pytest.mark.asyncio
async def test_process_source_local_file():
    """Test processing a local PDF file."""
    with patch('app.services.extract_service.extract_text_from_pdf') as mock_extract, \
         patch('app.services.extract_service.vllm.chat') as mock_chat, \
         patch('app.services.extract_service.settings') as mock_settings:
        
        mock_extract.return_value = "Product: Test Fund ISIN: TEST1234567"
        mock_settings.model = "test-model"
        mock_chat.return_value = {
            "choices": [{"message": {"content": '{"product_name": "Test Fund", "isin": "TEST1234567"}'}}]
        }
        
        result = await process_source("/path/to/local.pdf")
        
        assert isinstance(result, ExtractResult)
        assert result.success is True
        assert result.source == "/path/to/local.pdf"
        assert result.data.product_name == "Test Fund"
        assert result.data.isin == "TEST1234567"
        assert result.data.source_url == "/path/to/local.pdf"


@pytest.mark.asyncio
async def test_process_source_url():
    """Test processing a PDF URL."""
    with patch('app.services.extract_service.download_to_tmp') as mock_download, \
         patch('app.services.extract_service.extract_text_from_pdf') as mock_extract, \
         patch('app.services.extract_service.vllm.chat') as mock_chat, \
         patch('app.services.extract_service.settings') as mock_settings:
        
        mock_download.return_value = "/tmp/downloaded.pdf"
        mock_extract.return_value = "Product: Test Fund"
        mock_settings.model = "test-model"
        mock_chat.return_value = {
            "choices": [{"message": {"content": '{"product_name": "Test Fund"}'}}]
        }
        
        result = await process_source("https://example.com/doc.pdf")
        
        assert isinstance(result, ExtractResult)
        assert result.success is True
        assert result.source == "https://example.com/doc.pdf"
        assert result.data.source_url == "https://example.com/doc.pdf"


@pytest.mark.asyncio
async def test_process_source_invalid_json():
    """Test processing with invalid JSON response."""
    with patch('app.services.extract_service.extract_text_from_pdf') as mock_extract, \
         patch('app.services.extract_service.vllm.chat') as mock_chat, \
         patch('app.services.extract_service.settings') as mock_settings:
        
        mock_extract.return_value = "Test content"
        mock_settings.model = "test-model"
        mock_chat.return_value = {
            "choices": [{"message": {"content": "invalid json response"}}]
        }
        
        result = await process_source("/path/to/file.pdf")
        
        assert isinstance(result, ExtractResult)
        assert result.success is False
        assert result.error is not None


@pytest.mark.asyncio
async def test_process_source_exception():
    """Test processing with exception during PDF extraction."""
    with patch('app.services.extract_service.extract_text_from_pdf') as mock_extract:
        mock_extract.side_effect = Exception("PDF read error")
        
        result = await process_source("/path/to/file.pdf")
        
        assert isinstance(result, ExtractResult)
        assert result.success is False
        assert "PDF read error" in result.error


@pytest.mark.asyncio
async def test_extract_multiple_sources():
    """Test extracting from multiple sources."""
    with patch('app.services.extract_service.process_source') as mock_process:
        mock_process.side_effect = [
            ExtractResult(source="file1.pdf", success=True, data=PriipsFields(product_name="Fund 1")),
            ExtractResult(source="file2.pdf", success=False, error="Failed to read")
        ]
        
        request = ExtractRequest(sources=["file1.pdf", "file2.pdf"])
        results = await extract(request)
        
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
