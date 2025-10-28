#!/bin/bash
# Simplified Financial Reasoning Evaluation

BASE_URL="https://jeanbaptdzd-priips-llm-service.hf.space"

query_model() {
    local prompt="$1"
    echo "Query: $prompt" | head -c 80
    echo "..."
    
    # Use printf with %s for proper JSON escaping
    json_prompt=$(printf '%s' "$prompt" | jq -Rs .)
    
    curl -s -X POST "$BASE_URL/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"DragonLLM/qwen3-8b-fin-v1.0\",\"messages\":[{\"role\":\"system\",\"content\":\"You are a financial expert. Show your reasoning step by step.\"},{\"role\":\"user\",\"content\":$json_prompt}],\"max_tokens\":500,\"temperature\":0.3}" \
      --max-time 60 | python3 -c "import sys, json; data=json.load(sys.stdin); print('\n' + data['choices'][0]['message']['content'] + '\n')" 2>/dev/null || echo "Error"
}

echo "=========================================="
echo "Financial Reasoning Evaluation"
echo "=========================================="
echo ""

echo "Task 1: Investment Return Calculation"
echo "--------------------------------------"
query_model "Calculate: An investor bought 100 shares at €50, received €200 dividends over 2 years, sold at €65. What is the total return in euros and percentage? Show steps."
echo ""

echo "Task 2: Risk Suitability Assessment"
echo "------------------------------------"
query_model "A product has SRI 6/7, 5-year holding period, max loss -45%. Client: 28 years old, needs money in 2 years, low risk tolerance. Should they invest? Explain why."
echo ""

echo "Task 3: Fund Cost Comparison"
echo "-----------------------------"
query_model "Fund A: 5% entry fee, 0.5% annual fee. Fund B: 0% entry, 2% annual fee. Both return 8%. Which is better for €10,000 over 10 years? Calculate."
echo ""

echo "Task 4: Portfolio Rebalancing"
echo "------------------------------"
query_model "Portfolio was 60/40 stocks/bonds. Now 64.1/35.9 after gains. Transaction cost 0.5%, tax 30%. Should client rebalance? Consider pros/cons."
echo ""

echo "Task 5: PRIIPS Complexity"
echo "-------------------------"
query_model "What are the key challenges in creating a PRIIPS KID for a structured product with: 3 indices, 80% capital protection, 3-year lock-in, multiple cost layers?"
echo ""

echo "=========================================="
echo "Evaluation complete!"
echo "=========================================="
