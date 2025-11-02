#!/bin/bash

echo "="
echo "Testing Debug Endpoint - See actual prompt generation"
echo "================================================================="

echo -e "\n[Test 1] User message only (English)"
curl -s -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/debug/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ]
  }' | jq '.'

echo -e "\n\n================================================================="
echo "[Test 2] System + User (French)"
curl -s -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/debug/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Réponds EN FRANÇAIS SEULEMENT."},
      {"role": "user", "content": "Qu'"'"'est-ce qu'"'"'une obligation?"}
    ]
  }' | jq '.generated_prompt'

echo -e "\n\n================================================================="
echo "[Test 3] Check if system message appears in prompt"
response=$(curl -s -X POST "https://jeanbaptdzd-open-finance-llm-8b.hf.space/v1/debug/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "TEST SYSTEM MESSAGE HERE"},
      {"role": "user", "content": "Hello"}
    ]
  }')

echo "$response" | jq -r '.generated_prompt' | grep -q "TEST SYSTEM MESSAGE" && echo "✅ System message IS in prompt" || echo "❌ System message NOT in prompt"

echo -e "\nFull prompt:"
echo "$response" | jq -r '.generated_prompt'

