#!/bin/bash
# Test 1: English - should complete fully now
echo "============================================"
echo "TEST 1: English Complete Answer"
echo "============================================"
curl -s -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "Explain the Black-Scholes option pricing model, including its key assumptions and the main formula components."}],
    "max_tokens": 400,
    "temperature": 0.3
  }' | jq -r '.choices[0] | "Finish reason: \(.finish_reason)\nTokens: \(.usage // "N/A")\n\nAnswer:\n\(.message.content)"'

echo ""
echo ""
echo "============================================"
echo "TEST 2: French - Check language"
echo "============================================"
curl -s -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "DragonLLM/qwen3-8b-fin-v1.0",
    "messages": [{"role": "user", "content": "Expliquez le concept de diversification de portefeuille et son importance en gestion de patrimoine. Répondez en français."}],
    "max_tokens": 400,
    "temperature": 0.3
  }' | jq -r '.choices[0] | "Finish reason: \(.finish_reason)\nTokens: \(.usage // "N/A")\n\nAnswer:\n\(.message.content)"'
