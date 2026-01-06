#!/bin/bash
# Diagnostic script to check HF sync status
cd /Users/jeanbapt/simple-llm-pro-finance

echo "=== LOCAL BRANCH ===" 
git log --oneline main -3

echo ""
echo "=== REMOTES ==="
git remote -v

echo ""
echo "=== LOCAL DOCKERFILE (first 10 lines) ==="
head -10 Dockerfile

echo ""
echo "=== FORCE PUSH TO HF ==="
git push huggingface main:main --force -v 2>&1

echo ""
echo "=== DONE ==="

