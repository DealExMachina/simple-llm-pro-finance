#!/bin/bash
# Script to push changes to Hugging Face Space

set -e

echo "=== Checking Git Status ==="
git status

echo ""
echo "=== Checking Remotes ==="
git remote -v

echo ""
echo "=== Checking Branch ==="
git branch -vv

echo ""
echo "=== Last 3 Commits ==="
git log --oneline -3

echo ""
echo "=== Checking if files are deleted locally ==="
if [ -f "app/main.py" ]; then
    echo "❌ app/main.py still exists!"
else
    echo "✅ app/main.py is deleted"
fi

if [ -f "app/routers/openai_api.py" ]; then
    echo "❌ app/routers/openai_api.py still exists!"
else
    echo "✅ app/routers/openai_api.py is deleted"
fi

echo ""
echo "=== Fetching from huggingface remote ==="
git fetch huggingface

echo ""
echo "=== Comparing local vs remote ==="
echo "Commits in local but not in remote:"
git log --oneline huggingface/main..main 2>&1 | head -10

echo ""
echo "=== Attempting Push ==="
echo "Pushing to huggingface main:main..."
git push huggingface main:main 2>&1

echo ""
echo "=== Push Complete ==="
echo "Check the output above for any errors."
echo "If successful, go to https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b"
echo "and verify files are updated in the 'Files' tab."

