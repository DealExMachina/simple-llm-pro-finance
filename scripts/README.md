# Scripts

## `validate_hf_readme.py`

Validates that `README.md` is properly formatted for Hugging Face Spaces.

### Usage

```bash
# Run manually
python3 scripts/validate_hf_readme.py

# Automatically runs on git commit (via pre-commit hook)
git commit -m "Update README"
```

### What it validates

- ✅ YAML frontmatter exists and is properly formatted
- ✅ Required fields for Docker SDK (`sdk`, `app_port`)
- ✅ Valid values for `sdk`, `colorFrom`, `colorTo`, `suggested_hardware`
- ✅ Warns about deprecated fields (e.g., `hardware` → `suggested_hardware`)
- ✅ Recommends including `emoji` and `title` fields

### Pre-commit hook

The script is automatically run as a git pre-commit hook. If validation fails, the commit is aborted with error messages.

