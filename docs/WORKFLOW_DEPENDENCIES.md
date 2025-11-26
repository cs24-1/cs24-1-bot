# Workflow Dependencies

This document describes the dependency chain between GitHub Actions workflows in this project.

## Dependency Graph

```
Push to main (requirements-torch.txt changes)
    ↓
┌─────────────────────────────────┐
│ Build Base Docker Image         │
│ (build-base-image.yml)          │
└─────────────────────────────────┘
    ↓ (on completion: success)
    ├──────────────────────────────┐
    ↓                              ↓
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ Build CI Docker Image           │ │ Deploy Discord Bot              │
│ (ci-image.yml)                  │ │ (deploy.yml)                    │
└─────────────────────────────────┘ └─────────────────────────────────┘
    ↓ (on completion: success)
    ├──────────────────────────────┐
    ↓                              ↓
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ Testing Checks                  │ │ Linting Checks                  │
│ (test.yml)                      │ │ (lint.yml)                      │
└─────────────────────────────────┘ └─────────────────────────────────┘
```

## Workflow Details

### 1. Build Base Docker Image (`build-base-image.yml`)

**Triggers:**
- Push to `main` branch with changes to:
  - `requirements-torch.txt`
  - `docker/Dockerfile.base`
  - `.github/workflows/build-base-image.yml`
- Manual workflow dispatch

**Dependencies:** None (root workflow)

**Triggers downstream:**
- Build CI Docker Image
- Deploy Discord Bot

**Purpose:** Builds the base image with PyTorch dependencies

---

### 2. Build CI Docker Image (`ci-image.yml`)

**Triggers:**
- Push to `main` branch with changes to:
  - `requirements/requirements-torch.txt`
  - `requirements/requirements.txt`
  - `requirements/requirements-dev.txt`
  - `docker/Dockerfile.ci`
  - `.github/workflows/ci-image.yml`
- Manual workflow dispatch
- **Workflow run:** After "Build Base Docker Image" completes successfully

**Dependencies:** 
- Build Base Docker Image (when triggered via workflow_run)

**Triggers downstream:**
- Testing Checks
- Linting Checks

**Purpose:** Builds the CI image with all dependencies for testing/linting

**Behavior:**
- Runs on direct push/dispatch regardless of base image status
- Runs after base image build completes successfully
- Skips if triggered by workflow_run and base image build failed
- Builds for linux/amd64 platform only

---

### 3. Deploy Discord Bot (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- **Workflow run:** After "Build Base Docker Image" completes successfully

**Dependencies:** 
- Build Base Docker Image (when triggered via workflow_run)

**Triggers downstream:** None

**Purpose:** Builds and deploys the production bot image

**Behavior:**
- Runs on direct push regardless of base image status
- Runs after base image build completes successfully
- Skips if triggered by workflow_run and base image build failed
- Builds for linux/amd64 and linux/arm64 platforms

---

### 4. Testing Checks (`test.yml`)

**Triggers:**
- Pull request
- Manual workflow dispatch
- **Workflow run:** After "Build CI Docker Image" completes successfully

**Dependencies:** 
- Build CI Docker Image (when triggered via workflow_run)

**Triggers downstream:** None

**Purpose:** Runs pytest with coverage and posts coverage report as PR comment

**Behavior:**
- Uses pre-built CI image from registry (ghcr.io/cs24-1/cs24-1-bot-ci:latest)
- Runs on direct PR/dispatch regardless of CI image status
- Runs after CI image build completes successfully
- Skips if triggered by workflow_run and CI image build failed
- Generates JUnit XML and coverage reports
- Posts coverage report as PR comment (only changed files)
- Requires permissions: checks (write), contents (read), pull-requests (write), packages (read)

---

### 5. Linting Checks (`lint.yml`)

**Triggers:**
- Pull request
- Manual workflow dispatch
- **Workflow run:** After "Build CI Docker Image" completes successfully

**Dependencies:** 
- Build CI Docker Image (when triggered via workflow_run)

**Triggers downstream:** None

**Purpose:** Runs mypy, isort, and YAPF checks

**Behavior:**
- Uses pre-built CI image from registry (ghcr.io/cs24-1/cs24-1-bot-ci:latest)
- Runs on direct PR/dispatch regardless of CI image status
- Runs after CI image build completes successfully
- Skips if triggered by workflow_run and CI image build failed
- All checks use continue-on-error: true (non-blocking)
- Requires permissions: checks (write), contents (read), packages (read)

---

## Workflow Run Event Notes

### Important Limitations

1. **Branch context:** `workflow_run` events execute on the default branch, not the triggering branch
2. **Checkout required:** Must explicitly checkout code at the correct ref
3. **Permissions:** Inherits permissions from the default branch's workflow file
4. **Event payload:** Limited information about the triggering workflow

### Why This Matters

- Test/Lint workflows on PRs will **NOT** automatically re-run when CI image rebuilds
- They will only re-run when triggered by push to main after CI image rebuild
- For PR testing, the existing CI image in the registry is used

### Workaround for PR Re-testing

If CI image changes and you need to re-test an open PR:
1. Wait for CI image to rebuild on main
2. Merge main into your PR branch, OR
3. Manually trigger "Testing Checks" workflow via workflow_dispatch

---

## Related Documentation

- Docker image strategy: `docs/DOCKER_IMAGES.md`
- Implementation details: `docs/DOCKER_IMPLEMENTATION.md`
