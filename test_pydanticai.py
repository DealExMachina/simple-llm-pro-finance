#!/usr/bin/env python3
"""Test script for PydanticAI integration."""

import asyncio
import sys
from pydanticai_app.agents import finance_agent
from pydanticai_app.utils import extract_answer_from_reasoning, extract_key_terms


async def test_finance_agent():
    """Test the finance agent."""
    print("=" * 70)
    print("Testing PydanticAI Finance Agent")
    print("=" * 70)
    print()
    
    test_questions = [
        "Qu'est-ce qu'une obligation?",
        "Expliquez le concept de date de valeur.",
        "Qu'est-ce que le CAC 40?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"[{i}/{len(test_questions)}] Question: {question}")
        print("-" * 70)
        
        try:
            # Run agent
            result = await finance_agent.run(question)
            
            # Get raw response
            raw_response = result.output if hasattr(result, 'output') else str(result)
            
            # Extract answer from reasoning tags
            clean_answer = extract_answer_from_reasoning(str(raw_response))
            
            # Extract key terms
            key_terms = extract_key_terms(clean_answer)
            
            print(f"✅ Response received")
            print(f"Answer length: {len(clean_answer)} chars")
            print(f"Key terms: {key_terms[:5]}")
            print(f"Answer preview: {clean_answer[:200]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()
            return False
    
    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_finance_agent())
    sys.exit(0 if success else 1)

