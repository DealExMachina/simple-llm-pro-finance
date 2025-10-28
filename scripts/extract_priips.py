#!/usr/bin/env python3
"""
PRIIPS Document Extraction Script

Extracts text from PRIIPS KID PDFs and processes them for RAG context.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.pdf import extract_text_from_pdf


def extract_priips_document(pdf_path: Path, output_dir: Path) -> dict:
    """
    Extract content from a PRIIPS KID PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted content
        
    Returns:
        Dictionary with extracted content
    """
    print(f"📄 Processing: {pdf_path.name}")
    
    # Extract text from PDF
    try:
        raw_text = extract_text_from_pdf(pdf_path)
        print(f"✅ Extracted {len(raw_text)} characters")
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return None
    
    # Parse filename for metadata
    filename_parts = pdf_path.stem.split("_")
    isin = filename_parts[0] if len(filename_parts) > 0 else "UNKNOWN"
    product_name = filename_parts[1] if len(filename_parts) > 1 else pdf_path.stem
    
    # Create structured output
    extracted_data = {
        "metadata": {
            "filename": pdf_path.name,
            "extraction_date": datetime.now().isoformat(),
            "isin": isin,
            "product_name": product_name,
            "file_size_bytes": pdf_path.stat().st_size,
            "text_length": len(raw_text)
        },
        "raw_text": raw_text,
        "sections": extract_sections(raw_text)
    }
    
    # Save to JSON
    output_path = output_dir / f"{pdf_path.stem}_extracted.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to: {output_path}")
    return extracted_data


def extract_sections(text: str) -> dict:
    """
    Extract common PRIIPS KID sections from text.
    
    This is a simple implementation. Can be enhanced with LLM-based extraction.
    """
    sections = {}
    
    # Common PRIIPS section keywords
    keywords = {
        "summary": ["what is this product", "summary"],
        "objectives": ["objectives", "investment objectives"],
        "risk_indicator": ["risk indicator", "sri", "summary risk"],
        "performance_scenarios": ["performance scenarios", "what could i get"],
        "costs": ["what are the costs", "costs"],
        "holding_period": ["recommended holding period", "holding period"]
    }
    
    text_lower = text.lower()
    
    for section_name, search_terms in keywords.items():
        for term in search_terms:
            if term in text_lower:
                # Extract a snippet around the keyword
                start_idx = text_lower.find(term)
                # Get 500 chars after the keyword
                snippet = text[start_idx:start_idx + 500].strip()
                sections[section_name] = snippet
                break
    
    return sections


def batch_process_directory(input_dir: Path, output_dir: Path):
    """Process all PDFs in a directory."""
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {input_dir}")
        return
    
    print(f"📦 Found {len(pdf_files)} PDF files to process\n")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    for pdf_path in pdf_files:
        result = extract_priips_document(pdf_path, output_dir)
        if result:
            results.append(result)
        print()  # Blank line between files
    
    # Save summary
    summary_path = output_dir / "_extraction_summary.json"
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "total_processed": len(results),
        "total_failed": len(pdf_files) - len(results),
        "files": [r["metadata"] for r in results]
    }
    
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Processed {len(results)}/{len(pdf_files)} files successfully")
    print(f"📊 Summary saved to: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract PRIIPS KID documents for RAG context"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Input PDF file or directory containing PDFs"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: priips_documents/extracted/)"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    workspace_root = Path(__file__).parent.parent
    input_path = Path(args.input)
    
    if not input_path.is_absolute():
        input_path = workspace_root / input_path
    
    if args.output:
        output_dir = Path(args.output)
        if not output_dir.is_absolute():
            output_dir = workspace_root / output_dir
    else:
        output_dir = workspace_root / "priips_documents" / "extracted"
    
    # Process
    if input_path.is_file():
        output_dir.mkdir(parents=True, exist_ok=True)
        extract_priips_document(input_path, output_dir)
    elif input_path.is_dir():
        batch_process_directory(input_path, output_dir)
    else:
        print(f"❌ Error: {input_path} does not exist")
        sys.exit(1)


if __name__ == "__main__":
    main()

