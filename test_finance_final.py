#!/usr/bin/env python3
"""
Final finance tests with proper token limits and French language support.
"""

import httpx
import json
import time
from typing import Dict, Any, List

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

# English tests with increased token limits to handle thinking + answer
ENGLISH_TESTS = [
    {
        "category": "Financial Calculations",
        "question": "Calculate: If I invest $10,000 at 5% annual interest compounded annually for 3 years, what will be the final amount? Show your calculation and explain the formula.",
        "max_tokens": 300  # Increased for thinking + complete answer
    },
    {
        "category": "Risk Management",
        "question": "Define Value at Risk (VaR) and explain how it's used in portfolio management. Include examples.",
        "max_tokens": 350
    },
    {
        "category": "Options Trading",
        "question": "Explain call and put options. What are the key differences and when would you use each?",
        "max_tokens": 300
    },
]

# French tests with explicit language instructions
FRENCH_TESTS = [
    {
        "category": "Calculs Financiers",
        "question": "Si j'investis 10 000€ avec un taux d'intérêt annuel de 5% composé annuellement pendant 3 ans, quel sera le montant final? Montrez vos calculs et expliquez la formule. Répondez entièrement en français, y compris votre raisonnement.",
        "max_tokens": 300,
        "system_prompt": "Tu es un assistant financier qui répond toujours en français. Ton raisonnement et tes réponses doivent être entièrement en français."
    },
    {
        "category": "Gestion des Risques",
        "question": "Expliquez ce qu'est la VaR (Value at Risk / Valeur en Risque) et comment elle est utilisée dans la gestion de portefeuille. Donnez des exemples. Répondez entièrement en français.",
        "max_tokens": 350,
        "system_prompt": "Tu es un assistant financier qui répond toujours en français. Ton raisonnement et tes réponses doivent être entièrement en français."
    },
    {
        "category": "Options",
        "question": "Expliquez les options d'achat (call) et de vente (put). Quelles sont les différences clés et quand utiliser chacune? Répondez entièrement en français avec votre raisonnement en français.",
        "max_tokens": 300,
        "system_prompt": "Tu es un assistant financier qui répond toujours en français. Tout ton raisonnement interne et ta réponse finale doivent être en français."
    },
    {
        "category": "Termes Français",
        "question": "Expliquez les termes suivants de la bourse française: CAC 40, PEA, SICAV, et OAT. Pour chaque terme, donnez une définition claire. Répondez en français.",
        "max_tokens": 400,
        "system_prompt": "Tu es un expert en finance française. Réponds entièrement en français, y compris ton raisonnement."
    },
]

def run_test(test: Dict[str, Any], language: str = "English") -> Dict[str, Any]:
    """Run a single test."""
    print(f"\n{'='*80}")
    print(f"{'Catégorie' if language == 'French' else 'Category'}: {test['category']}")
    print(f"Question: {test['question'][:100]}...")
    print(f"Max Tokens: {test.get('max_tokens', 300)}")
    print(f"{'='*80}")
    
    messages = [{"role": "user", "content": test["question"]}]
    
    # Add system prompt for French tests
    if "system_prompt" in test:
        messages.insert(0, {"role": "system", "content": test["system_prompt"]})
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": test.get('max_tokens', 300)
    }
    
    start_time = time.time()
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=90.0
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            finish_reason = data['choices'][0].get('finish_reason', 'unknown')
            
            print(f"\n💬 Answer:")
            print(answer)
            
            print(f"\n📊 Stats:")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📝 Tokens: {usage.get('completion_tokens', 'N/A')}/{test.get('max_tokens', 300)}")
            print(f"   🏁 Finish: {finish_reason}")
            
            # Check if answer was complete
            is_complete = finish_reason == "stop"
            has_thinking = "<think>" in answer.lower()
            
            # For French tests, check if thinking is in French
            if language == "French":
                # Simple heuristic: check for French words in thinking section
                if has_thinking:
                    thinking_section = answer.split("</think>")[0].lower()
                    french_indicators = ["je", "le", "la", "est", "sont", "dans", "avec", "pour"]
                    english_indicators = ["the", "is", "are", "with", "for", "that"]
                    
                    french_count = sum(1 for word in french_indicators if word in thinking_section)
                    english_count = sum(1 for word in english_indicators if word in thinking_section)
                    
                    thinking_in_french = french_count > english_count
                    print(f"   🇫🇷 Thinking in French: {'✅' if thinking_in_french else '❌ (in English)'}")
            
            print(f"\n📈 Quality:")
            print(f"   {'✅' if is_complete else '⚠️  TRUNCATED'} Answer status: {finish_reason}")
            print(f"   {'✅' if has_thinking else '➖'} Shows reasoning: {has_thinking}")
            
            return {
                "success": True,
                "category": test['category'],
                "time": elapsed,
                "tokens_used": usage.get('completion_tokens', 0),
                "complete": is_complete,
                "has_reasoning": has_thinking
            }
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return {"success": False, "category": test['category'], "error": str(response.status_code)}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "category": test['category'], "error": str(e)}

def print_summary(results: List[Dict[str, Any]], language: str):
    """Print test summary."""
    print("\n" + "="*80)
    print("RÉSUMÉ" if language == "French" else "SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    complete = [r for r in successful if r.get('complete')]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"✅ Complete answers: {len(complete)}/{len(successful)} ({100*len(complete)/len(successful) if successful else 0:.1f}%)")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_tokens = sum(r['tokens_used'] for r in successful) / len(successful)
        
        print(f"\n📊 Metrics:")
        print(f"   ⏱️  Average time: {avg_time:.2f}s")
        print(f"   📝 Average tokens: {avg_tokens:.0f}")
        print(f"   🚀 Speed: {avg_tokens/avg_time:.2f} tokens/s")

def main():
    """Run all tests."""
    print("="*80)
    print("FINAL FINANCE LLM TESTS")
    print("="*80)
    print("Testing with proper token limits and language support")
    
    # English tests
    print("\n" + "="*80)
    print("ENGLISH TESTS")
    print("="*80)
    
    english_results = []
    for i, test in enumerate(ENGLISH_TESTS, 1):
        print(f"\n[Test {i}/{len(ENGLISH_TESTS)}]")
        result = run_test(test, "English")
        english_results.append(result)
        time.sleep(1)
    
    print_summary(english_results, "English")
    
    # French tests
    print("\n\n" + "="*80)
    print("FRENCH TESTS (with language instructions)")
    print("="*80)
    
    french_results = []
    for i, test in enumerate(FRENCH_TESTS, 1):
        print(f"\n[Test {i}/{len(FRENCH_TESTS)}]")
        result = run_test(test, "French")
        french_results.append(result)
        time.sleep(1)
    
    print_summary(french_results, "French")
    
    # Overall
    print("\n\n" + "="*80)
    print("OVERALL RESULTS")
    print("="*80)
    
    all_results = english_results + french_results
    all_successful = [r for r in all_results if r.get('success')]
    all_complete = [r for r in all_successful if r.get('complete')]
    
    print(f"\n📊 Total: {len(all_successful)}/{len(all_results)} successful")
    print(f"✅ Complete: {len(all_complete)}/{len(all_successful)} ({100*len(all_complete)/len(all_successful) if all_successful else 0:.1f}%)")
    print(f"🇬🇧 English: {len([r for r in english_results if r.get('success')])}/{len(ENGLISH_TESTS)}")
    print(f"🇫🇷 French: {len([r for r in french_results if r.get('success')])}/{len(FRENCH_TESTS)}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

