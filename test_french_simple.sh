#!/bin/bash
# Quick French test without system prompts

curl -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [
      {
        "role": "user", 
        "content": "Expliquez brièvement ce qu est une obligation (bond). Répondez en français."
      }
    ],
    "temperature": 0.3,
    "max_tokens": 400
  }' | jq -r '.choices[0].message.content' | head -50

echo ""
echo "====="
echo "Test 2: Financial calculation in French"
echo "====="

curl -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [
      {
        "role": "user",
        "content": "Si j investis 5000€ à 3% par an pendant 2 ans, quel sera le montant final? Répondez en français avec les calculs."
      }
    ],
    "temperature": 0.2,
    "max_tokens": 350
  }' | jq -r '.choices[0].message.content'
