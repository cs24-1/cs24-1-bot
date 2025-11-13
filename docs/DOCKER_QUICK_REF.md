# Docker Images Quick Reference

## Available Images

| Image | Registry URL | Purpose | Update Trigger |
|-------|-------------|---------|----------------|
| **Base** | `ghcr.io/cs24-1/cs24-1-bot-base:latest` | PyTorch foundation | `torch.requirements.txt` changes |
| **CI** | `ghcr.io/cs24-1/cs24-1-bot-ci:latest` | Testing & Linting | Requirements changes |
| **Production** | `ghcr.io/cs24-1/cs24-1-bot:latest` | Deployed bot | Push to main |
| **DevContainer** | Local only | Development env | Manual rebuild |

## Common Tasks

### Rebuild DevContainer
```bash
# In VS Code: Ctrl+Shift+P
# Then: "Dev Containers: Rebuild Container"
```

### Pull Latest Base Image Locally
```bash
docker pull ghcr.io/cs24-1/cs24-1-bot-base:latest
```

### Manually Trigger Image Build
1. Go to GitHub Actions tab
2. Select workflow:
   - "Build Base Docker Image" for base
   - "Build CI Docker Image" for CI
3. Click "Run workflow"
4. Select branch and confirm

### Check Image Build Status
```bash
# View all images in registry
gh api /orgs/cs24-1/packages
```

### Test Production Image Locally
```bash
# Pull and run
docker pull ghcr.io/cs24-1/cs24-1-bot:latest
docker run --env-file .env ghcr.io/cs24-1/cs24-1-bot:latest
```

## Troubleshooting

### "Error: pull access denied"
**Solution:** Authenticate with GitHub Container Registry
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### "CI image not found"
**Solution:** Manually trigger `ci-image.yml` workflow to build it

### "DevContainer build fails"
**Solution:** Check if base image exists and is accessible
```bash
docker pull ghcr.io/cs24-1/cs24-1-bot-base:latest
```

### "Production deploy slow"
**Solution:** Base image might be rebuilding. Check workflow logs.

## Image Sizes (Approximate)

- **Base**: ~3.5 GB (PyTorch is large)
- **CI**: ~4.0 GB (+ dev dependencies)
- **Production**: ~4.5 GB (+ app code)
- **DevContainer**: ~4.2 GB (+ dev tools)

## Update Frequency

- **Base**: Rarely (only when PyTorch version changes)
- **CI**: Occasionally (when dev dependencies change)
- **Production**: Every push to main
- **DevContainer**: Manual (when you rebuild)

## Related Documentation

- Full documentation: `docs/DOCKER_IMAGES.md`
- Implementation details: `docs/DOCKER_IMPLEMENTATION.md`
- Project setup: `README.md`
