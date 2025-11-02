#!/usr/bin/env python3
"""
🎯 Quiz Finance Français - Test de Compréhension
Évalue la maîtrise du modèle sur la terminologie financière française spécialisée
"""
import httpx
import json
import time
from datetime import datetime

BASE_URL = "https://jeanbaptdzd-open-finance-llm-8b.hf.space"

# Questions organisées par niveau de difficulté
QUIZ_QUESTIONS = {
    "Niveau 1 - Termes Bancaires Courants": [
        {
            "question": "Qu'est-ce qu'une date de valeur en banque?",
            "keywords": ["date", "effective", "compte", "opération", "crédit", "débit"],
            "difficulty": "⭐"
        },
        {
            "question": "Expliquez ce qu'est l'escompte bancaire.",
            "keywords": ["effet", "commerce", "échéance", "avance", "trésorerie"],
            "difficulty": "⭐"
        },
        {
            "question": "Qu'est-ce que la consignation en finance?",
            "keywords": ["somme", "dépôt", "tiers", "garantie", "conservé"],
            "difficulty": "⭐"
        }
    ],
    "Niveau 2 - Droit et Garanties": [
        {
            "question": "Définissez la main levée d'une hypothèque.",
            "keywords": ["hypothèque", "libération", "créancier", "bien", "garantie"],
            "difficulty": "⭐⭐"
        },
        {
            "question": "Qu'est-ce qu'un séquestre en droit financier?",
            "keywords": ["dépôt", "tiers", "litige", "neutre", "garantie"],
            "difficulty": "⭐⭐"
        },
        {
            "question": "Expliquez le nantissement de compte-titres.",
            "keywords": ["garantie", "créancier", "titres", "gage", "dette"],
            "difficulty": "⭐⭐"
        }
    ],
    "Niveau 3 - Instruments Financiers": [
        {
            "question": "Qu'est-ce qu'une créance douteuse pour une banque?",
            "keywords": ["crédit", "recouvrement", "risque", "défaut", "provision"],
            "difficulty": "⭐⭐⭐"
        },
        {
            "question": "Expliquez la portabilité du prêt immobilier.",
            "keywords": ["crédit", "établissement", "conditions", "transfert", "bien"],
            "difficulty": "⭐⭐⭐"
        },
        {
            "question": "Qu'est-ce qu'un covenant bancaire?",
            "keywords": ["clause", "engagement", "ratio", "financier", "respect"],
            "difficulty": "⭐⭐⭐"
        }
    ],
    "Niveau 4 - Fiscalité et Marchés": [
        {
            "question": "Définissez le portage salarial en France.",
            "keywords": ["indépendant", "salarié", "société", "prestation", "statut"],
            "difficulty": "⭐⭐⭐⭐"
        },
        {
            "question": "Qu'est-ce que le démembrement de propriété en finance?",
            "keywords": ["usufruit", "nue-propriété", "transmission", "fiscal", "donation"],
            "difficulty": "⭐⭐⭐⭐"
        },
        {
            "question": "Expliquez l'effet de levier en finance d'entreprise.",
            "keywords": ["dette", "capitaux propres", "rentabilité", "risque", "endettement"],
            "difficulty": "⭐⭐⭐⭐"
        }
    ],
    "Niveau 5 - Expert": [
        {
            "question": "Qu'est-ce qu'une créance privilégiée du Trésor Public?",
            "keywords": ["priorité", "recouvrement", "créanciers", "fiscal", "garantie"],
            "difficulty": "⭐⭐⭐⭐⭐"
        },
        {
            "question": "Définissez la clause de retour à meilleure fortune.",
            "keywords": ["dette", "suspension", "capacité", "remboursement", "financière"],
            "difficulty": "⭐⭐⭐⭐⭐"
        },
        {
            "question": "Expliquez le mécanisme du cantonnement de créances.",
            "keywords": ["séparation", "actifs", "risque", "véhicule", "titrisation"],
            "difficulty": "⭐⭐⭐⭐⭐"
        }
    ]
}

def extract_answer(content):
    """Extract answer from response (handle <think> tags)"""
    if "</think>" in content:
        return content.split("</think>", 1)[1].strip()
    return content.strip()

def check_comprehension(answer, keywords):
    """Check if answer demonstrates comprehension"""
    answer_lower = answer.lower()
    
    # Count how many keywords are present
    keywords_found = sum(1 for kw in keywords if kw.lower() in answer_lower)
    
    # Calculate score
    keyword_coverage = (keywords_found / len(keywords)) * 100
    
    # Check answer quality
    has_french = any(c in answer for c in ["é", "è", "ê", "à", "ç", "ù"])
    is_substantial = len(answer) > 100
    
    return {
        "keywords_found": keywords_found,
        "keywords_total": len(keywords),
        "keyword_coverage": keyword_coverage,
        "has_french": has_french,
        "is_substantial": is_substantial,
        "score": min(100, keyword_coverage + (20 if is_substantial else 0))
    }

def ask_question(question_data):
    """Ask a question to the model"""
    try:
        response = httpx.post(
            f"{BASE_URL}/v1/chat/completions",
            json={
                "model": "DragonLLM/qwen3-8b-fin-v1.0",
                "messages": [
                    {"role": "user", "content": question_data["question"]}
                ],
                # Use default max_tokens (1500) for complete answers
                # "max_tokens": 600,  # Removed to use server default
                "temperature": 0.3
            },
            timeout=90.0
        )
        
        data = response.json()
        if "error" in data:
            return {"error": data["error"]["message"]}
        
        content = data["choices"][0]["message"]["content"]
        answer = extract_answer(content)
        
        # Check comprehension
        comprehension = check_comprehension(answer, question_data["keywords"])
        
        return {
            "answer": answer,
            "full_response": content,
            "comprehension": comprehension,
            "finish_reason": data["choices"][0].get("finish_reason", "unknown")
        }
        
    except Exception as e:
        return {"error": str(e)}

def display_result(question_num, total_questions, question_data, result):
    """Display a single question result"""
    print(f"\n{'='*80}")
    print(f"Question {question_num}/{total_questions} {question_data['difficulty']}")
    print(f"{'='*80}")
    print(f"❓ {question_data['question']}")
    
    if "error" in result:
        print(f"\n❌ Erreur: {result['error']}")
        return 0
    
    comp = result["comprehension"]
    answer = result["answer"]
    
    print(f"\n💬 Réponse du modèle:")
    print(f"{answer}")  # Show COMPLETE answer
    print(f"\n📏 Longueur: {len(answer)} caractères")
    
    print(f"\n📊 Évaluation:")
    print(f"  • Mots-clés trouvés: {comp['keywords_found']}/{comp['keywords_total']}")
    print(f"  • Couverture: {comp['keyword_coverage']:.1f}%")
    print(f"  • En français: {'✅' if comp['has_french'] else '❌'}")
    print(f"  • Réponse substantielle: {'✅' if comp['is_substantial'] else '❌'}")
    
    # Score interpretation
    score = comp['score']
    if score >= 80:
        grade = "🌟 Excellent"
        emoji = "✅"
    elif score >= 60:
        grade = "👍 Bien"
        emoji = "✅"
    elif score >= 40:
        grade = "😐 Moyen"
        emoji = "⚠️"
    else:
        grade = "❌ Insuffisant"
        emoji = "❌"
    
    print(f"\n{emoji} Score: {score:.1f}/100 - {grade}")
    
    return score

def run_quiz(mode="full"):
    """Run the finance quiz"""
    print("="*80)
    print("🎯 QUIZ FINANCE FRANÇAIS - ÉVALUATION DU MODÈLE")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🤖 Modèle: DragonLLM/qwen3-8b-fin-v1.0")
    print(f"🎚️  Mode: {mode}")
    print("="*80)
    
    all_scores = []
    level_scores = {}
    total_questions = 0
    current_question = 0
    
    # Count total questions
    for level, questions in QUIZ_QUESTIONS.items():
        total_questions += len(questions)
    
    # Run quiz
    for level, questions in QUIZ_QUESTIONS.items():
        print(f"\n\n{'🔥'*40}")
        print(f"📚 {level}")
        print(f"{'🔥'*40}")
        
        level_scores[level] = []
        
        for question_data in questions:
            current_question += 1
            
            print(f"\n⏳ Interrogation du modèle...")
            result = ask_question(question_data)
            
            score = display_result(current_question, total_questions, question_data, result)
            
            all_scores.append(score)
            level_scores[level].append(score)
            
            # Small delay between questions
            if current_question < total_questions:
                time.sleep(2)
    
    # Final summary
    print("\n\n" + "="*80)
    print("📈 RÉSULTATS FINAUX")
    print("="*80)
    
    for level, scores in level_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        print(f"\n{level}")
        print(f"  Score moyen: {avg_score:.1f}/100")
        print(f"  Détail: {', '.join(f'{s:.0f}' for s in scores)}")
    
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"\n{'='*80}")
    print(f"🏆 SCORE GLOBAL: {overall_avg:.1f}/100")
    print(f"{'='*80}")
    
    # Grade
    if overall_avg >= 80:
        grade = "🌟 EXCELLENT - Maîtrise parfaite de la finance française"
        emoji = "🥇"
    elif overall_avg >= 70:
        grade = "👍 TRÈS BIEN - Bonne compréhension des termes techniques"
        emoji = "🥈"
    elif overall_avg >= 60:
        grade = "✅ BIEN - Compréhension correcte"
        emoji = "🥉"
    elif overall_avg >= 50:
        grade = "😐 MOYEN - Compréhension partielle"
        emoji = "📚"
    else:
        grade = "❌ INSUFFISANT - Nécessite des améliorations"
        emoji = "📖"
    
    print(f"\n{emoji} {grade}")
    
    # Recommendations
    print(f"\n💡 Analyse:")
    excellent_count = sum(1 for s in all_scores if s >= 80)
    good_count = sum(1 for s in all_scores if 60 <= s < 80)
    medium_count = sum(1 for s in all_scores if 40 <= s < 60)
    poor_count = sum(1 for s in all_scores if s < 40)
    
    print(f"  • Excellentes réponses: {excellent_count}/{total_questions}")
    print(f"  • Bonnes réponses: {good_count}/{total_questions}")
    print(f"  • Réponses moyennes: {medium_count}/{total_questions}")
    print(f"  • Réponses insuffisantes: {poor_count}/{total_questions}")
    
    if overall_avg >= 70:
        print(f"\n✅ Le modèle démontre une excellente maîtrise de la terminologie")
        print(f"   financière française, y compris les termes techniques spécialisés.")
    elif overall_avg >= 60:
        print(f"\n👍 Le modèle comprend bien la terminologie financière française.")
        print(f"   Quelques améliorations possibles sur les termes les plus techniques.")
    else:
        print(f"\n⚠️  Le modèle peut s'améliorer sur certains termes techniques.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    run_quiz(mode)

