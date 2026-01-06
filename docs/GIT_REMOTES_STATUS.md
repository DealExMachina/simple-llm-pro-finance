# Git Remotes Status

## Configured Remotes

1. **`origin`** → `https://github.com/DealExMachina/simple-llm-pro-finance.git`
   - Primary GitHub repository (DealExMachina org)
   - Used for: Main development, CI/CD

2. **`huggingface`** → `https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b`
   - Hugging Face Spaces repository
   - Used for: HF Space deployment
   - **Current branch `main` tracks `huggingface/main`**

3. **`dragon-llm`** → `https://github.com/Dragon-LLM/simple-llm-pro-finance.git`
   - Secondary GitHub repository (Dragon-LLM org)
   - Used for: Backup/sync

## Current Issue

The HF Space is still installing the old version because:
- ✅ Local `Dockerfile` has been updated to use `vllm/vllm-openai:latest`
- ❓ Changes may not have been pushed to `huggingface` remote
- ❓ HF Space pulls from `huggingface/main` branch

## Action Required

To update the HF Space with the vLLM changes:

```bash
# 1. Verify local changes are committed
git status

# 2. Push to Hugging Face remote (this triggers HF Space rebuild)
git push huggingface main:main

# 3. Optionally sync to other remotes
git push origin main
git push dragon-llm main
```

## Branch Tracking

- `main` branch → tracks `huggingface/main`
- `master` branch → tracks `origin/master`
- `dev` branch → tracks `origin/main`

