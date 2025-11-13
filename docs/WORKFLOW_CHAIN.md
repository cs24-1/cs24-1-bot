# Workflow Dependency Chain - Quick View

## Complete Dependency Flow

```
┌────────────────────────────────────────────────────────────────┐
│  TRIGGER: Push to main (torch.requirements.txt changes)        │
└────────────────────────────────────────────────────────────────┘
                              ↓
        ╔═════════════════════════════════════════╗
        ║  Build Base Docker Image (15 min)       ║  ← ROOT
        ║  (PyTorch + Python 3.12)                ║
        ╚═════════════════════════════════════════╝
                    ↓ (on success)
        ┌───────────┴───────────┐
        ↓                       ↓
╔═══════════════════════╗  ╔═══════════════════════╗
║ Build CI Image (5min) ║  ║ Deploy Bot (8 min)    ║
║ (+ app + dev deps)    ║  ║ (+ app code)          ║
╚═══════════════════════╝  ╚═══════════════════════╝
        ↓ (on success)
    ┌───┴───┐
    ↓       ↓
┌─────────┐ ┌─────────┐
│ Test    │ │ Lint    │  ← LEAF NODES
│ (2 min) │ │ (1 min) │
└─────────┘ └─────────┘
```

## Key Points

### ✅ Dependencies Now Configured

1. **CI Image Build** → waits for **Base Image Build** ✓
2. **Deploy** → waits for **Base Image Build** ✓
3. **Test** → waits for **CI Image Build** ✓
4. **Lint** → waits for **CI Image Build** ✓

### 🎯 How It Works

- **workflow_run trigger**: Workflows listen for completion of upstream workflows
- **Conditional execution**: Only runs if upstream workflow succeeded
- **Direct triggers still work**: Push/PR/manual triggers bypass dependency checks

### ⚡ Execution Modes

| Trigger | Base | CI | Deploy | Test | Lint |
|---------|------|----|----|------|------|
| **Push to main (PyTorch change)** | ✓ | ✓¹ | ✓¹ | ✓² | ✓² |
| **Push to main (app change)** | - | ✓ | ✓ | ✓¹ | ✓¹ |
| **Pull Request** | - | - | - | ✓ | ✓ |
| **Manual: Base** | ✓ | ✓¹ | - | ✓² | ✓² |
| **Manual: CI** | - | ✓ | - | ✓¹ | ✓¹ |

¹ = Triggered after upstream success  
² = Triggered after CI build success (which waits for Base)

### 📋 Example Timeline

**Scenario: Update PyTorch version**

```
00:00 - Push torch.requirements.txt to main
00:00 - Base Image Build starts
15:00 - Base Image Build completes ✓
15:01 - CI Image Build starts (auto-triggered)
15:01 - Deploy starts (auto-triggered)
20:01 - CI Image Build completes ✓
22:01 - Test starts (auto-triggered)
22:01 - Lint starts (auto-triggered)
23:01 - Deploy completes ✓
24:01 - Test completes ✓
24:01 - Lint completes ✓
```

**Total: ~24 minutes** (vs. ~60+ min if all ran independently)

### 🔄 Smart Caching

- Each workflow caches its build layers
- Subsequent runs use cached layers when possible
- Only changed layers are rebuilt

### 🚨 Failure Handling

```
Base Build FAILS
    ↓
CI Build: SKIPPED
Deploy: SKIPPED
Test: Uses old CI image (if exists)
Lint: Uses old CI image (if exists)
```

```
CI Build FAILS (Base succeeded)
    ↓
Test: SKIPPED
Lint: SKIPPED
Deploy: CONTINUES (doesn't depend on CI)
```

### 💡 Pro Tips

1. **PR Testing**: Uses existing CI image from registry, no rebuilds
2. **Force Rebuild**: Use workflow_dispatch (manual trigger)
3. **Check Status**: Go to Actions tab to see dependency chain
4. **Emergency Deploy**: Push will trigger deploy even if images building

## Related Docs

- Full details: `docs/WORKFLOW_DEPENDENCIES.md`
- Docker strategy: `docs/DOCKER_IMAGES.md`
