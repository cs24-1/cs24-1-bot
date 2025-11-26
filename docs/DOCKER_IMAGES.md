# Docker Image Strategy

This project uses a multi-layered Docker image strategy to optimize build times and resource usage across development, CI/CD, and production environments.

## Image Hierarchy

```
python:3.12-slim
    ↓
cs24-1-bot-base (requirements-torch.txt)
    ↓
    ├── cs24-1-bot-ci (requirements.txt + requirements-dev.txt)
    ├── cs24-1-bot (requirements.txt + app code)
    └── devcontainer (requirements.txt + requirements-dev.txt + dev tools)
```

## Images

### 1. Base Image (`docker/Dockerfile.base`)

**Image:** `ghcr.io/cs24-1/cs24-1-bot-base:latest`

**Contains:**
- Python 3.12 slim
- PyTorch and torchvision (from `requirements-torch.txt`)
- System timezone configuration

**Build trigger:** Changes to `requirements/requirements-torch.txt` or `docker/Dockerfile.base`

**Platforms:** linux/amd64, linux/arm64

**Usage:** Foundation for all other images to avoid rebuilding heavy PyTorch dependencies

### 2. CI Image (`docker/Dockerfile.ci`)

**Image:** `ghcr.io/cs24-1/cs24-1-bot-ci:latest`

**Contains:**
- Base image
- Application dependencies (`requirements.txt`)
- Development dependencies (`requirements-dev.txt`)

**Build trigger:** Changes to requirements files or `docker/Dockerfile.ci`

**Platform:** linux/amd64 (GitHub Actions runners)

**Usage:** Used in testing and linting workflows

### 3. Production Image (`docker/Dockerfile`)

**Image:** `ghcr.io/cs24-1/cs24-1-bot:latest`

**Contains:**
- Base image
- Application dependencies (`requirements.txt`)
- Application code
- Runtime configuration

**Build trigger:** Push to `main` branch or base image rebuild

**Platforms:** linux/amd64, linux/arm64

**Usage:** Deployed Discord bot

### 4. DevContainer Image (`.devcontainer/Dockerfile`)

**Image:** Built locally (not pushed to registry)

**Contains:**
- Base image
- Application dependencies (`requirements.txt`)
- Development dependencies (`requirements-dev.txt`)
- GPG for commit signing
- VS Code extensions

**Build trigger:** DevContainer rebuild

**Usage:** Local development environment

## Workflows

### `build-base-image.yml`

Builds and pushes the base image with PyTorch dependencies.

- **Triggers:** 
  - Push to `main` with changes to `requirements/requirements-torch.txt` or `docker/Dockerfile.base`
  - Manual workflow dispatch
- **Artifacts:** `ghcr.io/cs24-1/cs24-1-bot-base:latest`

### `ci-image.yml`

Builds and pushes the CI image with all testing/linting dependencies.

- **Triggers:**
  - Push to `main` with changes to requirements files or `docker/Dockerfile.ci`
  - Manual workflow dispatch
- **Artifacts:** `ghcr.io/cs24-1/cs24-1-bot-ci:latest`

### `deploy.yml`

Builds and pushes the production image.

- **Triggers:**
  - Push to `main`
  - Completion of base image build
- **Artifacts:** `ghcr.io/cs24-1/cs24-1-bot:latest`

### `test.yml` and `lint.yml`

Run tests and linting using the pre-built CI image.

- **Triggers:** Pull requests
- **Uses:** `ghcr.io/cs24-1/cs24-1-bot-ci:latest`

## Manual Rebuilds

To manually trigger a rebuild of the base or CI images:

1. Go to Actions tab in GitHub
2. Select "Build Base Docker Image" or "Build CI Docker Image"
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## Local Development

The devcontainer uses the base image from the registry. If you need to test base image changes locally:

1. Build the base image locally:
   ```bash
   docker build -f docker/Dockerfile.base -t ghcr.io/cs24-1/cs24-1-bot-base:latest .
   ```

2. Rebuild the devcontainer in VS Code:
   - Press `Ctrl+Shift+P`
   - Select "Dev Containers: Rebuild Container"

## Image Permissions

All images are stored in GitHub Container Registry (ghcr.io) and require authentication:

- Public read access for pulling
- Write access requires `GITHUB_TOKEN` (automatically provided in workflows)
- Manual pulls may require personal access token (PAT)

## Troubleshooting

### CI jobs fail with "image not found"

The CI image might not exist yet. Manually trigger the `ci-image.yml` workflow to build it.

### Base image outdated

If PyTorch or system dependencies are outdated:
1. Update `requirements-torch.txt`
2. Push to `main` or manually trigger `build-base-image.yml`
3. Wait for rebuild to complete
4. Subsequent jobs will use the new base image
