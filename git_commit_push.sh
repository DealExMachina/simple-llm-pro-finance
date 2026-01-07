#!/bin/bash
# Commit and push cleanup changes
set -e
# Change to repository root (works from any subdirectory)
cd "$(git rev-parse --show-toplevel)" || exit 1

echo "=== Git Status ==="
git status

echo ""
echo "=== Staging all changes ==="
git add -A

echo ""
echo "=== Committing ==="
git commit -m "chore: Clean up repository - remove obsolete files and directories

- Remove 9 obsolete troubleshooting docs
- Remove temporary scripts (check_hf_sync.sh, commit_and_push.sh, etc.)
- Remove empty app subdirectories (middleware, providers, routers, services)
- Remove unused OpenAI models (app/models/openai.py)
- Remove test_openai_models.py (tested removed models)
- Remove llama.cpp directory (not needed with vLLM)
- Remove old venv directory
- Update .gitignore
- Keep: config files, utils, integration tests, benchmarks, GGUF scripts"

echo ""
echo "=== Pushing to HuggingFace ==="
git push huggingface main

echo ""
echo "=== Pushing to origin (GitHub) ==="
git push origin main

echo ""
echo "=== Pushing to dragon-llm ==="
git push dragon-llm main

echo ""
echo "=== Done! ==="

# Self-destruct
rm -f git_commit_push.sh

