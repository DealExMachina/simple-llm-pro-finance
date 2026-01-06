# Manual Push Instructions for HF Space

## Problem

The push to Hugging Face Space (`huggingface` remote) is not working. The remote files are not updating.

## Solution: Manual Push

Run these commands **manually** in your terminal:

```bash
cd /Users/jeanbapt/simple-llm-pro-finance

# 1. Check current status
git status
git log --oneline -3

# 2. Verify files are deleted locally
ls app/main.py  # Should say "No such file or directory"
ls app/routers/openai_api.py  # Should say "No such file or directory"

# 3. Ensure all changes are committed
git add -A
git status  # Should show no uncommitted changes

# 4. Fetch from remote to see what's there
git fetch huggingface

# 5. Compare local vs remote
git log --oneline huggingface/main..main  # Shows commits not in remote

# 6. Push to HF Space
git push huggingface main:main

# If that doesn't work, try force push (CAUTION: only if you're sure)
# git push huggingface main:main --force
```

## Alternative: Use the Script

I've created a diagnostic script:

```bash
cd /Users/jeanbapt/simple-llm-pro-finance
./push-to-hf.sh
```

This will:
- Check git status
- Verify files are deleted
- Compare local vs remote
- Attempt the push
- Show any errors

## Verify Push Success

After pushing, check:

1. **HF Space Files Tab**: https://huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b
   - Go to "Files" tab
   - Verify `app/main.py` is **NOT** there
   - Verify `Dockerfile` shows `FROM vllm/vllm-openai:latest`

2. **Git Log**: 
   ```bash
   git fetch huggingface
   git log --oneline huggingface/main -3
   ```
   Should show your recent commits

## Common Issues

### Issue 1: Authentication Error
If you see authentication errors:
- Check your HF token in `.git/config` under `[remote "huggingface"]`
- Token might be expired
- May need to regenerate HF token

### Issue 2: Permission Denied
- Verify you have write access to the Space
- Check Space settings for permissions

### Issue 3: Remote Not Found
- Verify remote exists: `git remote -v`
- Should show: `huggingface → https://hf_...@huggingface.co/spaces/jeanbaptdzd/open-finance-llm-8b`

### Issue 4: Branch Mismatch
- Check which branch Space is tracking
- May need to push to different branch: `git push huggingface main:master`

## Force Push (Last Resort)

**⚠️ WARNING**: Only use if you're certain:

```bash
git push huggingface main:main --force
```

This will overwrite the remote branch. Use only if:
- You're sure local is correct
- Remote has old/incorrect code
- You've verified local files are correct

## After Successful Push

1. **Wait for Auto-Rebuild**: HF Space should automatically detect push and rebuild
2. **Or Manual Rebuild**: Go to Space Settings → Rebuild Space
3. **Check Logs**: Should show vLLM startup, not FastAPI

## Expected Result

After successful push and rebuild, logs should show:
```
==========================================
vLLM OpenAI Server - Starting
==========================================
🌐 Detected Hugging Face Spaces environment
Tool Calling: ENABLED (parser: hermes)
```

**NOT:**
- ❌ `INFO:app.main:`
- ❌ `Uvicorn running`
- ❌ `Initializing Transformers`

