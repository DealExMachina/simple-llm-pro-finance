# Docker Hub Setup for GitHub Actions

## Required GitHub Repository Configuration

To enable Docker Hub authentication in GitHub Actions, you need to configure the following:

### 1. Repository Variables

Go to: **Settings → Secrets and variables → Actions → Variables tab**

Add a repository variable:
- **Name**: `DOCKERHUB_USER`
- **Value**: Your Docker Hub username (e.g., `jeanbapt`)

### 2. Repository Secrets

Go to: **Settings → Secrets and variables → Actions → Secrets tab**

Add a repository secret:
- **Name**: `DOCKERHUB_ACCESS_KEY`
- **Value**: Your Docker Hub access token (not your password!)

### 3. Creating a Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings → Security → New Access Token**
3. Give it a name (e.g., "GitHub Actions")
4. Set permissions: **Read & Write** (needed to push images)
5. Copy the token immediately (you won't see it again)
6. Paste it into the GitHub secret `DOCKERHUB_ACCESS_KEY`

### 4. Verify Configuration

The workflow uses:
- `vars.DOCKERHUB_USER` → Your Docker Hub username
- `secrets.DOCKERHUB_ACCESS_KEY` → Your Docker Hub access token

### 5. Troubleshooting

If builds fail with authentication errors:

1. **Check the secret exists**: Go to Settings → Secrets and verify `DOCKERHUB_ACCESS_KEY` is set
2. **Check the variable exists**: Go to Settings → Variables and verify `DOCKERHUB_USER` is set
3. **Verify token permissions**: The token must have **Read & Write** permissions
4. **Check token expiration**: Access tokens don't expire, but you can revoke and recreate them
5. **Verify username**: Make sure `DOCKERHUB_USER` matches your Docker Hub username exactly

### 6. Testing Authentication

After setup, trigger a workflow run. The "🔐 Log in to Docker Hub" step should succeed. If it fails, check:
- The secret value is correct (no extra spaces)
- The variable value matches your Docker Hub username
- The access token has the correct permissions

