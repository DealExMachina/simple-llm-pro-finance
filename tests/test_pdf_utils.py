import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

from app.utils.pdf import download_to_tmp, extract_text_from_pdf


@pytest.mark.asyncio
async def test_download_to_tmp_success():
    """Test successful PDF download."""
    url = "https://example.com/document.pdf"
    tmp_dir = Path("/tmp")
    mock_content = b"PDF content here"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.content = mock_content
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await download_to_tmp(url, tmp_dir)
        
        assert isinstance(result, Path)
        assert result.name == "document.pdf"
        assert result.parent == tmp_dir


@pytest.mark.asyncio
async def test_download_to_tmp_no_filename():
    """Test download with URL that has no filename."""
    url = "https://example.com/"
    tmp_dir = Path("/tmp")
    mock_content = b"PDF content"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.content = mock_content
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await download_to_tmp(url, tmp_dir)
        
        assert isinstance(result, Path)
        assert result.name == "document.pdf"  # Default filename
        assert result.parent == tmp_dir


@pytest.mark.asyncio
async def test_download_to_tmp_http_error():
    """Test download with HTTP error."""
    url = "https://example.com/document.pdf"
    tmp_dir = Path("/tmp")
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.content = b"PDF content"
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(Exception):
            await download_to_tmp(url, tmp_dir)


def test_extract_text_from_pdf_success():
    """Test successful PDF text extraction."""
    pdf_path = Path("/tmp/test.pdf")
    expected_text = "Sample PDF content"
    
    with patch('app.utils.pdf.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = expected_text
        
        result = extract_text_from_pdf(pdf_path)
        
        assert result == expected_text


def test_extract_text_from_pdf_multiple_pages():
    """Test PDF text extraction from multiple pages."""
    pdf_path = Path("/tmp/test.pdf")
    expected_text = "Page 1 content\nPage 2 content\nPage 3 content"
    
    with patch('app.utils.pdf.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = expected_text
        
        result = extract_text_from_pdf(pdf_path)
        
        assert result == expected_text


def test_extract_text_from_pdf_import_error():
    """Test PDF extraction when PyMuPDF is not available."""
    pdf_path = Path("/tmp/test.pdf")
    
    with patch('app.utils.pdf.extract_text_from_pdf', side_effect=RuntimeError("PyMuPDF (fitz) is required")):
        with pytest.raises(RuntimeError, match="PyMuPDF.*required"):
            extract_text_from_pdf(pdf_path)


def test_extract_text_from_pdf_file_error():
    """Test PDF extraction with file read error."""
    pdf_path = Path("/tmp/test.pdf")
    
    with patch('app.utils.pdf.extract_text_from_pdf', side_effect=RuntimeError("PyMuPDF (fitz) is required")):
        with pytest.raises(RuntimeError, match="PyMuPDF.*required"):
            extract_text_from_pdf(pdf_path)
