# Workflow Dependencies

This document describes the dependency chain between GitHub Actions workflows in this project.

## Dependency Graph

```
Push to main (torch.requirements.txt changes)
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
- Push with changes to:
  - `torch.requirements.txt`
  - `Dockerfile.base`
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
- Push with changes to:
  - `torch.requirements.txt`
  - `requirements.txt`
  - `requirements-dev.txt`
  - `Dockerfile.ci`
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

---

### 3. Deploy Discord Bot (`deploy.yml`)

**Triggers:**
- Push to branch (currently any branch for testing)
- **Workflow run:** After "Build Base Docker Image" completes successfully

**Dependencies:** 
- Build Base Docker Image (when triggered via workflow_run)

**Triggers downstream:** None

**Purpose:** Builds and deploys the production bot image

**Behavior:**
- Runs on direct push regardless of base image status
- Runs after base image build completes successfully
- Skips if triggered by workflow_run and base image build failed

---

### 4. Testing Checks (`test.yml`)

**Triggers:**
- Pull request
- Manual workflow dispatch
- **Workflow run:** After "Build CI Docker Image" completes successfully

**Dependencies:** 
- Build CI Docker Image (when triggered via workflow_run)

**Triggers downstream:** None

**Purpose:** Runs pytest with coverage

**Behavior:**
- Uses pre-built CI image from registry
- Runs on direct PR/dispatch regardless of CI image status
- Runs after CI image build completes successfully
- Skips if triggered by workflow_run and CI image build failed

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
- Uses pre-built CI image from registry
- Runs on direct PR/dispatch regardless of CI image status
- Runs after CI image build completes successfully
- Skips if triggered by workflow_run and CI image build failed

---

## Execution Scenarios

### Scenario 1: PyTorch Dependency Update

```
1. Developer updates torch.requirements.txt
2. Pushes to main
3. Build Base Docker Image triggers (15 min)
   ├─> On success: Build CI Docker Image triggers (5 min)
   │   ├─> On success: Testing Checks triggers (2 min)
   │   └─> On success: Linting Checks triggers (1 min)
   └─> On success: Deploy Discord Bot triggers (8 min)
```

**Total time:** ~31 minutes (sequential execution)

---

### Scenario 2: Application Dependency Update

```
1. Developer updates requirements.txt
2. Pushes to main
3. Build CI Docker Image triggers (5 min)
   ├─> On success: Testing Checks triggers (2 min)
   └─> On success: Linting Checks triggers (1 min)
4. Deploy Discord Bot triggers independently (8 min)
```

**Total time:** ~8 minutes (parallel execution of CI and Deploy)

---

### Scenario 3: Pull Request

```
1. Developer opens PR
2. Testing Checks triggers (2 min)
3. Linting Checks triggers (2 min)
```

**Total time:** ~2 minutes (parallel execution)

**Note:** Uses existing CI image from registry, no rebuilds needed

---

### Scenario 4: Manual Workflow Trigger

```
1. Developer manually triggers "Build Base Docker Image"
2. Build Base Docker Image runs (15 min)
   └─> On success: Build CI Docker Image triggers (5 min)
       ├─> On success: Testing Checks triggers (2 min)
       └─> On success: Linting Checks triggers (1 min)
```

**Note:** Deploy does NOT trigger (requires push event)

---

## Conditional Execution

All dependent workflows use conditional execution to ensure they only run when upstream workflows succeed:

### Pattern 1: Direct Push or Successful Workflow Run
```yaml
if: ${{ github.event_name == 'push' || github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}
```

Used by:
- Build CI Docker Image
- Deploy Discord Bot

**Behavior:** Runs immediately on direct push/dispatch, OR waits for upstream workflow success

### Pattern 2: Skip on Failed Workflow Run
```yaml
if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}
```

Used by:
- Testing Checks
- Linting Checks

**Behavior:** Always runs on direct trigger (PR/dispatch), but skips if upstream workflow failed

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

## Monitoring Workflow Dependencies

### Check Workflow Status
```bash
# Via GitHub CLI
gh run list --workflow=build-base-image.yml
gh run list --workflow=ci-image.yml
gh run list --workflow=deploy.yml
```

### View Dependency Chain
```bash
# View all workflow runs
gh run list --limit 20

# Watch specific workflow
gh run watch <run-id>
```

### Debug Failed Dependencies
```bash
# View logs of failed run
gh run view <run-id> --log-failed
```

---

## Best Practices

### When to Use Manual Triggers

- **Base Image:** After manual changes to Dockerfile.base
- **CI Image:** After adding new dev dependencies
- **Deploy:** Never (should be automatic on main push)
- **Test/Lint:** To re-run checks without pushing new commits

### Handling Failed Builds

1. **Base image fails:**
   - Fix the issue
   - Push fix or manually re-trigger
   - CI image and Deploy will NOT run until base succeeds

2. **CI image fails:**
   - Fix the issue  
   - Push fix or manually re-trigger
   - Test/Lint will NOT run until CI succeeds
   - Deploy continues independently (doesn't depend on CI image)

3. **Deploy fails:**
   - No downstream impact
   - Fix and re-trigger deploy

4. **Test/Lint fails:**
   - No downstream impact (leaf nodes)
   - Fix code and push to PR

---

## Future Improvements

Potential enhancements to the workflow dependency chain:

1. **Composite workflows:** Combine related workflows into a single reusable workflow
2. **Matrix builds:** Test against multiple Python versions simultaneously
3. **Artifact sharing:** Pass build artifacts between workflows instead of rebuilding
4. **Smarter triggers:** Only rebuild images when dependencies actually change (hash-based)
5. **Notification system:** Alert on workflow failures in the dependency chain

---

## Related Documentation

- Docker image strategy: `docs/DOCKER_IMAGES.md`
- Implementation details: `docs/DOCKER_IMPLEMENTATION.md`
- Quick reference: `docs/DOCKER_QUICK_REF.md`
