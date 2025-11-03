# CodeRabbit Setup Troubleshooting

## Issue: CodeRabbit not appearing in PRs

### Step 1: Verify Installation

1. Go to: https://github.com/marketplace/coderabbitai
2. Click "Install it for free" or "Configure access"
3. Make sure it's installed for your organization/user
4. Verify it has access to `DealExMachina/simple-llm-pro-finance`

### Step 2: Check Repository Settings

1. Go to: https://github.com/DealExMachina/simple-llm-pro-finance/settings/installations
2. Look for "CodeRabbitAI" in installed GitHub Apps
3. Click "Configure" next to it
4. Ensure this repository is selected (or "All repositories")

### Step 3: Check Webhooks

1. Go to: https://github.com/DealExMachina/simple-llm-pro-finance/settings/hooks
2. Look for a webhook pointing to: `https://app.coderabbit.ai/githubHandler`
3. If missing, CodeRabbit should create it automatically, but you can check

### Step 4: Test with a Real PR

CodeRabbit may need:
- **Code changes** (not just docs)
- **Multiple files** changed
- **Python files** to review

Try this:

```bash
# Create a test PR with actual code changes
git checkout -b test-coderabbit-code
# Make a small code change (add a comment, fix formatting)
# Then create PR
```

### Step 5: Check PR for CodeRabbit Bot

- Look for user: `@coderabbitai` or `@coderabbit`
- Check "Conversation" tab in PR
- Sometimes it takes 2-5 minutes to appear

### Step 6: Manual Trigger

Try adding this to your PR description:
```
@coderabbitai please review
```

Or mention it:
```
@coderabbit please review this PR
```

### Step 7: Verify Configuration File

The `.coderabbit.yaml` file has been created. CodeRabbit should respect this configuration.

### Alternative: Use CodeRabbit Comments

If CodeRabbit is installed but not auto-commenting, try:
1. Comment in the PR: `/review` or `/review_code`
2. Or use: `/ask @coderabbitai review this PR`

## Still Not Working?

1. Check CodeRabbit status: https://status.coderabbit.ai/
2. Review CodeRabbit docs: https://docs.coderabbit.ai/
3. Contact support: https://coderabbit.ai/support

## What CodeRabbit Should Review:

- Code quality and best practices
- Security vulnerabilities
- Performance issues
- Python-specific patterns
- Error handling
- Documentation completeness

