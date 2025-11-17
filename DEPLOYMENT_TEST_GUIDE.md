# Deployment and Testing Guide

## Quick Test Summary

All critical issues have been fixed and new features added. Here's how to test them:

## ✅ Changes Made

1. **Health Endpoint** - Now includes `model_ready` status
2. **Error Sanitization** - Internal errors no longer leak details
3. **Rate Limiting** - 30 req/min, 500 req/hour (demo-friendly)
4. **Statistics Tracking** - New `/v1/stats` endpoint
5. **Improved Token Counting** - More accurate token tracking
6. **Constants Extracted** - All magic numbers moved to constants

## 🧪 Testing Options

### Option 1: Quick Deployment Test (No Model Required)

```bash
# Start server (if not already running)
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run deployment test script
./test_deployment.sh

# Or test against deployed instance
export API_URL=https://your-space.hf.space
./test_deployment.sh
```

### Option 2: Python Test Script

```bash
# Start server first
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run test script
python test_new_features.py
```

### Option 3: Manual Testing

#### 1. Test Health Endpoint
```bash
curl http://localhost:8080/health
```

**Expected Response:**
```json
{
  "status": "healthy" or "initializing",
  "service": "LLM Pro Finance API",
  "model_ready": true or false
}
```

#### 2. Test Stats Endpoint
```bash
curl http://localhost:8080/v1/stats
```

**Expected Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 0,
  "total_tokens": 0,
  "average_total_tokens": 0.0,
  "requests_per_hour": 0.0,
  "tokens_per_hour": 0.0,
  ...
}
```

#### 3. Test Rate Limiting Headers
```bash
curl -I http://localhost:8080/v1/models
```

**Expected Headers:**
```
X-RateLimit-Limit-Minute: 30
X-RateLimit-Limit-Hour: 500
X-RateLimit-Remaining-Minute: 29
X-RateLimit-Remaining-Hour: 499
```

#### 4. Test Error Sanitization
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[]}'
```

**Expected:** 400 error with clear message, no internal details

#### 5. Test Rate Limiting (Trigger 429)
```bash
# Make 31 requests quickly
for i in {1..31}; do
  curl -s http://localhost:8080/v1/models > /dev/null
done
```

**Expected:** 31st request returns 429 with `Retry-After` header

## 🚀 Deployment to Hugging Face Spaces

### Automatic Deployment
If using Hugging Face Spaces, push to the repository and it will auto-deploy:

```bash
git add .
git commit -m "feat: Add rate limiting, stats tracking, and fix critical issues"
git push origin main
```

### Manual Verification After Deployment

1. **Check Health:**
   ```bash
   curl https://your-username-open-finance-llm-8b.hf.space/health
   ```

2. **Check Stats:**
   ```bash
   curl https://your-username-open-finance-llm-8b.hf.space/v1/stats
   ```

3. **Make a Test Request:**
   ```bash
   curl -X POST https://your-username-open-finance-llm-8b.hf.space/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "DragonLLM/qwen3-8b-fin-v1.0",
       "messages": [{"role": "user", "content": "What is compound interest?"}],
       "max_tokens": 500
     }'
   ```

4. **Check Stats Again:**
   ```bash
   curl https://your-username-open-finance-llm-8b.hf.space/v1/stats
   ```
   Should show 1 request and token counts.

## 📊 What to Verify

### ✅ Health Endpoint
- [ ] Returns `model_ready` field
- [ ] Status is "healthy" when model loaded, "initializing" otherwise

### ✅ Stats Endpoint
- [ ] Returns comprehensive statistics
- [ ] Token counts increment after requests
- [ ] Request counts increment correctly
- [ ] Averages calculated correctly

### ✅ Rate Limiting
- [ ] Headers present in responses
- [ ] 429 returned when limit exceeded
- [ ] `Retry-After` header present on 429
- [ ] Limits reset after time window

### ✅ Error Handling
- [ ] Validation errors return 400 with clear messages
- [ ] Internal errors return 500 with sanitized messages
- [ ] No stack traces or file paths in error responses

### ✅ Token Counting
- [ ] Token counts in responses match stats
- [ ] Both streaming and non-streaming tracked
- [ ] Token counts are reasonable (not 0 or extremely high)

## 🐛 Troubleshooting

### Import Errors
If you see import errors, ensure:
- All dependencies installed: `pip install -r requirements.txt`
- Virtual environment activated
- Python path includes project root

### Rate Limiting Not Working
- Check middleware is registered in `app/main.py`
- Verify rate limit constants in `app/utils/constants.py`
- Check logs for middleware execution

### Stats Not Updating
- Ensure stats tracker is imported in provider
- Check that requests are being recorded
- Verify stats endpoint is accessible (public path)

### Health Check Shows "initializing"
- Model may still be loading (check logs)
- Model initialization may have failed (check logs)
- Wait a few minutes and check again

## 📝 Test Results Template

After testing, document results:

```
Date: [DATE]
Environment: [Local/Docker/HF Space]
Model Status: [Loaded/Initializing/Failed]

Health Endpoint: ✅/❌
Stats Endpoint: ✅/❌
Rate Limiting: ✅/❌
Error Handling: ✅/❌
Token Counting: ✅/❌

Notes:
- [Any issues found]
- [Performance observations]
- [Recommendations]
```

## 🎯 Next Steps

1. Run deployment tests
2. Verify all endpoints work
3. Test rate limiting behavior
4. Monitor stats endpoint
5. Deploy to production
6. Monitor logs for any issues

