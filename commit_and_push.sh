#!/bin/bash
# Script to commit and push vLLM migration changes to HF

set -e
cd /Users/jeanbapt/simple-llm-pro-finance

echo "=== Git Status ==="
git status

echo ""
echo "=== Staging all changes ==="
git add -A

echo ""
echo "=== Committing ==="
git commit -m "feat: Migrate HF Spaces to vLLM, add Langfuse support

- Replace Transformers-based Dockerfile with vLLM base image
- Add Langfuse and Logfire to both Dockerfiles  
- Unify deployment between HF Spaces and Koyeb
- Remove obsolete FastAPI app code
- Clean up requirements.txt"

echo ""
echo "=== Pushing to HuggingFace ==="
git push huggingface main --force

echo ""
echo "=== Pushing to origin (GitHub DealExMachina) ==="
git push origin main

echo ""
echo "=== Pushing to dragon-llm (GitHub Dragon-LLM) ==="
git push dragon-llm main

echo ""
echo "=== Done! ==="

