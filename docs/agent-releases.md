# Agent Release Files for GitHub

This document explains how to create GitHub releases with agent download files so that the download links in the web interface work correctly.

## File Naming Convention

The agent download URLs follow this pattern:
```
https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-{platform}-{architecture}{extension}
```

### Required Files

The following files must be uploaded as assets to GitHub releases:

#### Windows
- `malsift-agent-windows-x86.exe`
- `malsift-agent-windows-x64.exe`

#### Linux
- `malsift-agent-linux-x86.tar.gz`
- `malsift-agent-linux-x64.tar.gz`
- `malsift-agent-linux-arm64.tar.gz`

#### macOS
- `malsift-agent-macos-x64.tar.gz`
- `malsift-agent-macos-arm64.tar.gz`

## Creating Placeholder Files

To generate placeholder files with the correct names:

```bash
./scripts/create-agent-release-files.sh
```

This will create a `release-assets/` directory with all the required placeholder files.

## Creating a GitHub Release

1. **Build your agent binaries** for each platform/architecture
2. **Replace the placeholder files** in `release-assets/` with your actual binaries
3. **Create a GitHub release**:
   - Go to: https://github.com/malsiftcyber/MalsiftCND/releases/new
   - Create a new tag (e.g., `v1.0.0` or `agent-v1.0.0`)
   - Add release title and description
   - Upload all files from `release-assets/` as release assets
   - Publish the release

## Using the "latest" Release URL

The web interface uses `/releases/latest/download/` URLs. For these to work:

- **Option 1**: Tag your release as `latest` (GitHub will redirect `/latest` to the most recent release)
- **Option 2**: Ensure your release is the most recent release in the repository

## Verifying Downloads

After creating a release, verify the download URLs work:

```bash
# Test Windows x64 download
curl -L -o test.exe https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-windows-x64.exe

# Test Linux x64 download
curl -L -o test.tar.gz https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-linux-x64.tar.gz

# Test macOS arm64 download
curl -L -o test.tar.gz https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-macos-arm64.tar.gz
```

## Notes

- GitHub release assets must have **exact filenames** matching the URL pattern
- File extensions are important: `.exe` for Windows, `.tar.gz` for Linux/macOS
- The `/latest/download/` URL will automatically redirect to the most recent release
- If you need to update agent files, create a new release (GitHub doesn't allow editing release assets)

