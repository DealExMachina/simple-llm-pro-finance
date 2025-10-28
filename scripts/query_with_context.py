#!/usr/bin/env python3
"""
Query LLM with PRIIPS Document Context

Loads extracted PRIIPS documents and queries the LLM with RAG context.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict
import requests

# Configuration
BASE_URL = "https://jeanbaptdzd-priips-llm-service.hf.space"
MODEL = "DragonLLM/qwen3-8b-fin-v1.0"


def load_extracted_documents(extracted_dir: Path) -> List[Dict]:
    """Load all extracted PRIIPS documents."""
    documents = []
    
    for json_file in extracted_dir.glob("*_extracted.json"):
        if json_file.name.startswith("_"):
            continue  # Skip summary files
        
        with open(json_file, "r", encoding="utf-8") as f:
            documents.append(json.load(f))
    
    return documents


def build_context(documents: List[Dict], query: str, max_chars: int = 2000) -> str:
    """
    Build RAG context from documents relevant to the query.
    
    Simple implementation: include all document summaries.
    Can be enhanced with semantic search/embeddings.
    """
    context_parts = []
    total_chars = 0
    
    for doc in documents:
        metadata = doc["metadata"]
        
        # Build a summary of this document
        doc_summary = f"\n--- Document: {metadata['product_name']} (ISIN: {metadata['isin']}) ---\n"
        
        # Include extracted sections
        if "sections" in doc and doc["sections"]:
            for section_name, content in doc["sections"].items():
                if content:
                    section_text = f"\n{section_name.upper()}:\n{content[:300]}...\n"
                    doc_summary += section_text
        
        # Check if we have space
        if total_chars + len(doc_summary) > max_chars:
            break
        
        context_parts.append(doc_summary)
        total_chars += len(doc_summary)
    
    if not context_parts:
        return "No relevant documents found."
    
    return "\n".join(context_parts)


def query_llm(query: str, context: str, max_tokens: int = 500) -> str:
    """Query the LLM with context."""
    
    # Build the prompt with context
    prompt = f"""You are a financial expert assistant specializing in PRIIPS Key Information Documents.

Use the following context from PRIIPS documents to answer the question:

{context}

Question: {query}

Provide a clear, accurate answer based on the context provided. If the context doesn't contain enough information, say so."""
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a PRIIPS financial document expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3  # Lower temperature for more factual responses
    }
    
    print(f"🔍 Querying LLM with {len(context)} chars of context...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        
        # Print usage stats
        usage = data.get("usage", {})
        print(f"📊 Tokens used: {usage.get('total_tokens', 'N/A')}")
        
        return answer
        
    except Exception as e:
        return f"Error querying LLM: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Query LLM with PRIIPS document context"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Question to ask about PRIIPS documents"
    )
    parser.add_argument(
        "--extracted-dir",
        type=str,
        default="priips_documents/extracted",
        help="Directory containing extracted documents"
    )
    parser.add_argument(
        "--max-context",
        type=int,
        default=2000,
        help="Maximum context characters to include"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="Maximum tokens in response"
    )
    
    args = parser.parse_args()
    
    # Setup paths
    workspace_root = Path(__file__).parent.parent
    extracted_dir = workspace_root / args.extracted_dir
    
    if not extracted_dir.exists():
        print(f"❌ Directory not found: {extracted_dir}")
        print("Run extract_priips.py first to extract documents.")
        sys.exit(1)
    
    # Load documents
    print(f"📚 Loading documents from {extracted_dir}...")
    documents = load_extracted_documents(extracted_dir)
    
    if not documents:
        print("⚠️  No extracted documents found.")
        print("Add PDFs to priips_documents/raw/ and run extract_priips.py")
        sys.exit(1)
    
    print(f"✅ Loaded {len(documents)} documents")
    
    # Build context
    context = build_context(documents, args.query, args.max_context)
    
    # Query LLM
    print(f"\n❓ Question: {args.query}\n")
    answer = query_llm(args.query, context, args.max_tokens)
    
    print(f"\n💬 Answer:\n{answer}\n")


if __name__ == "__main__":
    main()

