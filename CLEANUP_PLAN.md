# Code Cleanup Plan

## Overview
This document outlines the cleanup strategy for the simple-llm-pro-finance project to remove obsolete files and improve code organization.

## Files to Remove

### 1. Obsolete Test Scripts (Root Directory)
**Reason:** All functional tests have been moved to `tests/` directory. These are one-off debugging scripts.

- `analyze_performance.py` - Performance analysis done, results in FINAL_TEST_REPORT.md
- `debug_chat_template.py` - Debug script, no longer needed
- `final_clean_test.py` - One-off test
- `investigate_french_consistency.py` - Investigation complete
- `quiz_finance_francais.py` - Test script (also in git staging)
- `test_advanced_finance.py` - Moved to tests/
- `test_all_fixes.py` - One-off validation
- `test_debug_endpoint.sh` - Shell test script
- `test_finance_final.py` - One-off test
- `test_finance_improved.py` - One-off test
- `test_finance_queries.py` - One-off test
- `test_french_direct.py` - One-off test
- `test_french_final_check.py` - One-off test
- `test_french_simple.sh` - Shell test script
- `test_french_strategies.py` - One-off test
- `test_generation_fix.sh` - Shell test script
- `test_memory_stress.py` - Moved to tests/
- `test_quick_french.py` - One-off test
- `test_service.py` - One-off test
- `test_system_prompt.py` - One-off test
- `test_tokenizer_debug.py` - Debug script
- `test_truncation_issue.py` - One-off test

**Total:** 21 test files

### 2. Obsolete Documentation Files
**Reason:** Superseded by comprehensive final reports.

- `STATUS.md` - Historical status, superseded by FINAL_STATUS.md
- `FIXES_SUMMARY.md` - Historical, covered in FINAL_TEST_REPORT.md
- `PERFORMANCE_REPORT.md` - Covered in FINAL_TEST_REPORT.md
- `memory_test_results.txt` - Old test results
- `test_results.txt` - Old test results

**Total:** 5 documentation files

### 3. Empty/Debug Code Directories
**Reason:** Unused or debug-only code.

- `app/utils/` - Empty directory (only __pycache__)
- `app/routers/debug.py` - Debug endpoint not needed in production

**Total:** 1 directory, 1 file

## Files to Keep

### Core Application
- `app/` directory (except items listed for removal)
  - `main.py` - FastAPI application
  - `config.py` - Configuration
  - `middleware.py` - API key authentication
  - `models/openai.py` - Pydantic models
  - `providers/base.py` - Provider protocol
  - `providers/transformers_provider.py` - Main inference engine
  - `routers/openai_api.py` - OpenAI-compatible API
  - `services/chat_service.py` - Chat service wrapper

### Tests
- `tests/` directory - Proper pytest structure
  - `conftest.py`
  - `test_config.py`
  - `test_middleware.py`
  - `test_openai_models.py`
  - `test_openai_routes.py`
  - `test_providers.py`
  - `performance/` - Performance benchmarks

### Documentation
- `README.md` - Main documentation (needs cleanup)
- `FINAL_STATUS.md` - Final deployment status
- `FINAL_TEST_REPORT.md` - Comprehensive test results
- `LICENSE` - MIT license

### Configuration & Deployment
- `Dockerfile` - Docker build configuration
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies

### Scripts
- `scripts/validate_hf_readme.py` - Useful validation utility
- `scripts/README.md` - Scripts documentation

## Refactoring Needed

### 1. Remove Debug Router from Production
**File:** `app/main.py`
**Change:** Remove debug router import and mount
```python
# Remove this line
app.include_router(debug.router, prefix="/v1")
```

### 2. Clean Up README.md
**File:** `README.md`
**Changes:**
- Remove outdated test coverage stats (91% reference)
- Update to reflect current stable state
- Simplify configuration section
- Remove references to obsolete features

### 3. Remove Empty Utils Directory
**Directory:** `app/utils/`
**Action:** Delete the entire directory as it's unused

## Impact Assessment

### Breaking Changes
**None** - All removed files are development/debugging artifacts.

### Non-Breaking Changes
- Removing debug endpoint (`/v1/debug/prompt`) - Not documented in README
- Cleaner project structure
- Reduced repository size

### Benefits
- **Clarity:** Easier to understand project structure
- **Maintenance:** Fewer files to maintain
- **Size:** Reduced repo size
- **Professionalism:** Clean, production-ready codebase

## Execution Plan

1. ✅ Create backup branch
2. ✅ Remove obsolete test files
3. ✅ Remove obsolete documentation
4. ✅ Remove debug code
5. ✅ Update README.md
6. ✅ Run tests to verify nothing broke
7. ✅ Commit and push changes

## Success Criteria

- ✅ All tests in `tests/` directory still pass
- ✅ Application still starts and serves requests
- ✅ README.md is accurate and up-to-date
- ✅ No broken imports or references
- ✅ Git history preserved (files deleted, not rewritten)

## Rollback Plan

If issues arise:
1. Git checkout the cleanup branch: `git checkout pre-cleanup-backup`
2. Review what was removed
3. Restore only necessary files

