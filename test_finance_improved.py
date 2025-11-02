#!/usr/bin/env python3
"""
Improved finance tests with better prompts for concise, complete answers.
"""

import httpx
import json
import time
from typing import Dict, Any, List

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

# Improved finance tests with prompts that encourage concise but complete answers
FINANCE_TESTS = [
    {
        "category": "Financial Calculations",
        "question": "Calculate: If I invest $10,000 at 5% annual interest compounded annually for 3 years, what will be the final amount? Show your calculation steps briefly.",
        "max_tokens": 150
    },
    {
        "category": "Risk Management", 
        "question": "Define Value at Risk (VaR) and explain its main use in portfolio management. Be concise but complete.",
        "max_tokens": 200
    },
    {
        "category": "Financial Instruments",
        "question": "Explain the key difference between call and put options in 2-3 sentences.",
        "max_tokens": 100
    },
    {
        "category": "Market Analysis",
        "question": "List 5 key factors that influence stock market volatility and briefly explain each.",
        "max_tokens": 250
    },
    {
        "category": "Corporate Finance",
        "question": "Compare EBITDA vs Net Income: What's included in each and why does the difference matter?",
        "max_tokens": 200
    },
    {
        "category": "Investment Strategy",
        "question": "Explain portfolio diversification and why it's important. Give a concrete example.",
        "max_tokens": 200
    },
    {
        "category": "Financial Ratios",
        "question": "How do you calculate P/E ratio? What does a high vs low P/E tell you about a stock?",
        "max_tokens": 150
    },
    {
        "category": "Fixed Income",
        "question": "Explain the inverse relationship between bond prices and interest rates. Why does this occur?",
        "max_tokens": 150
    },
]

# French finance tests with proper French terminology
FRENCH_FINANCE_TESTS = [
    {
        "category": "Calculs Financiers",
        "question": "Si j'investis 10 000€ avec un taux d'intérêt annuel de 5% composé annuellement pendant 3 ans, quel sera le montant final? Montrez vos calculs.",
        "max_tokens": 150
    },
    {
        "category": "Gestion des Risques",
        "question": "Expliquez ce qu'est la VaR (Value at Risk / Valeur en Risque) et son utilisation dans la gestion de portefeuille.",
        "max_tokens": 200
    },
    {
        "category": "Instruments Financiers",
        "question": "Quelle est la différence entre une option d'achat (call) et une option de vente (put)?",
        "max_tokens": 150
    },
    {
        "category": "Analyse Boursière",
        "question": "Quels sont les principaux facteurs qui influencent la volatilité des marchés boursiers?",
        "max_tokens": 200
    },
    {
        "category": "Finance d'Entreprise",
        "question": "Expliquez la différence entre l'EBITDA (Bénéfice avant intérêts, impôts, dépréciation et amortissement) et le résultat net.",
        "max_tokens": 200
    },
    {
        "category": "Stratégie d'Investissement",
        "question": "Qu'est-ce que la diversification d'un portefeuille et pourquoi est-elle importante?",
        "max_tokens": 200
    },
    {
        "category": "Ratios Financiers",
        "question": "Comment calculer le ratio cours/bénéfice (PER) et comment l'interpréter?",
        "max_tokens": 150
    },
    {
        "category": "Obligations",
        "question": "Pourquoi les prix des obligations baissent-ils lorsque les taux d'intérêt augmentent?",
        "max_tokens": 150
    },
    {
        "category": "Analyse Technique (Termes Français)",
        "question": "Expliquez les termes suivants utilisés en bourse française: CAC 40, PEA, sicav, et OAT.",
        "max_tokens": 200
    },
    {
        "category": "Fiscalité (France)",
        "question": "Quelle est la différence entre la Flat Tax et le barème progressif pour l'imposition des revenus de capitaux mobiliers en France?",
        "max_tokens": 200
    },
]

def run_test(test: Dict[str, Any], language: str = "English") -> Dict[str, Any]:
    """Run a single test."""
    print(f"\n{'─'*80}")
    print(f"Catégorie: {test['category']}" if language == "French" else f"Category: {test['category']}")
    print(f"Question: {test['question']}")
    print(f"Max Tokens: {test.get('max_tokens', 200)}")
    print(f"{'─'*80}")
    
    payload = {
        "model": "DragonLLM/qwen3-8b-fin-v1.0",
        "messages": [
            {"role": "user", "content": test["question"]}
        ],
        "temperature": 0.2,  # Lower for more focused answers
        "max_tokens": test.get('max_tokens', 200)
    }
    
    start_time = time.time()
    
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=60.0
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            finish_reason = data['choices'][0].get('finish_reason', 'unknown')
            
            print(f"\n📊 Stats:")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   📝 Tokens: {usage.get('completion_tokens', 'N/A')}/{test.get('max_tokens', 200)}")
            print(f"   🏁 Finish: {finish_reason}")
            
            print(f"\n💬 Answer:\n{answer}")
            
            # Evaluate answer quality
            is_complete = finish_reason == "stop"
            has_thinking = "<think>" in answer
            answer_content = answer.split("</think>")[-1].strip() if has_thinking else answer
            
            print(f"\n📈 Quality:")
            print(f"   {'✅' if is_complete else '⚠️'} Complete: {is_complete}")
            print(f"   {'✅' if has_thinking else '➖'} Shows reasoning: {has_thinking}")
            print(f"   📏 Answer length: {len(answer_content)} chars")
            
            return {
                "success": True,
                "category": test['category'],
                "time": elapsed,
                "tokens_used": usage.get('completion_tokens', 0),
                "tokens_limit": test.get('max_tokens', 200),
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
    print("RÉSUMÉ DES TESTS" if language == "French" else "TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_tokens = sum(r['tokens_used'] for r in successful) / len(successful)
        complete_count = sum(1 for r in successful if r.get('complete'))
        reasoning_count = sum(1 for r in successful if r.get('has_reasoning'))
        
        print(f"\n📊 Performance Metrics:")
        print(f"   ⏱️  Average response time: {avg_time:.2f}s")
        print(f"   📝 Average tokens used: {avg_tokens:.0f}")
        print(f"   ✅ Complete answers: {complete_count}/{len(successful)} ({100*complete_count/len(successful):.1f}%)")
        print(f"   🧠 Answers with reasoning: {reasoning_count}/{len(successful)} ({100*reasoning_count/len(successful):.1f}%)")
        
        # Token efficiency
        total_used = sum(r['tokens_used'] for r in successful)
        total_limit = sum(r['tokens_limit'] for r in successful)
        print(f"   💰 Token efficiency: {total_used}/{total_limit} ({100*total_used/total_limit:.1f}% utilization)")

def main():
    """Run all tests."""
    print("="*80)
    print("IMPROVED FINANCE LLM TESTING")
    print("="*80)
    print(f"Target: {BASE_URL}")
    
    # Test English questions
    print("\n" + "="*80)
    print("ENGLISH FINANCE TESTS (Improved Prompts)")
    print("="*80)
    
    english_results = []
    for i, test in enumerate(FINANCE_TESTS, 1):
        print(f"\n[Test {i}/{len(FINANCE_TESTS)}]")
        result = run_test(test, "English")
        english_results.append(result)
        if i < len(FINANCE_TESTS):
            time.sleep(1)
    
    print_summary(english_results, "English")
    
    # Test French questions
    print("\n\n" + "="*80)
    print("FRENCH FINANCE TESTS (Questions en Français)")
    print("="*80)
    print("Testing with French finance terminology...")
    
    french_results = []
    for i, test in enumerate(FRENCH_FINANCE_TESTS, 1):
        print(f"\n[Test {i}/{len(FRENCH_FINANCE_TESTS)}]")
        result = run_test(test, "French")
        french_results.append(result)
        if i < len(FRENCH_FINANCE_TESTS):
            time.sleep(1)
    
    print_summary(french_results, "French")
    
    # Overall summary
    print("\n\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    
    total_tests = len(english_results) + len(french_results)
    total_success = sum(1 for r in english_results + french_results if r.get('success'))
    
    print(f"\n📊 Total Tests: {total_tests}")
    print(f"✅ Total Successful: {total_success}/{total_tests} ({100*total_success/total_tests:.1f}%)")
    print(f"🇬🇧 English: {len([r for r in english_results if r.get('success')])}/{len(english_results)}")
    print(f"🇫🇷 French: {len([r for r in french_results if r.get('success')])}/{len(french_results)}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

