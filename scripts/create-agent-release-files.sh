#!/bin/bash
# Script to create placeholder agent files for GitHub releases
# These files should be uploaded as assets when creating a GitHub release

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create release files directory
RELEASE_DIR="release-assets"
mkdir -p "$RELEASE_DIR"

print_status "Creating placeholder agent files for GitHub releases..."
print_warning "These are placeholder files. Replace them with actual agent binaries when creating releases."

# Windows agents
print_status "Creating Windows agent files..."
echo "Placeholder Windows x86 agent binary" > "$RELEASE_DIR/malsift-agent-windows-x86.exe"
echo "Placeholder Windows x64 agent binary" > "$RELEASE_DIR/malsift-agent-windows-x64.exe"

# Linux agents
print_status "Creating Linux agent files..."
echo "Placeholder Linux x86 agent archive" | gzip > "$RELEASE_DIR/malsift-agent-linux-x86.tar.gz" 2>/dev/null || \
    (echo "Placeholder Linux x86 agent archive" > "$RELEASE_DIR/malsift-agent-linux-x86.tar" && \
     gzip "$RELEASE_DIR/malsift-agent-linux-x86.tar" 2>/dev/null || echo "Note: gzip not available, created .tar file")

echo "Placeholder Linux x64 agent archive" | gzip > "$RELEASE_DIR/malsift-agent-linux-x64.tar.gz" 2>/dev/null || \
    (echo "Placeholder Linux x64 agent archive" > "$RELEASE_DIR/malsift-agent-linux-x64.tar" && \
     gzip "$RELEASE_DIR/malsift-agent-linux-x64.tar" 2>/dev/null || echo "Note: gzip not available, created .tar file")

echo "Placeholder Linux arm64 agent archive" | gzip > "$RELEASE_DIR/malsift-agent-linux-arm64.tar.gz" 2>/dev/null || \
    (echo "Placeholder Linux arm64 agent archive" > "$RELEASE_DIR/malsift-agent-linux-arm64.tar" && \
     gzip "$RELEASE_DIR/malsift-agent-linux-arm64.tar" 2>/dev/null || echo "Note: gzip not available, created .tar file")

# macOS agents
print_status "Creating macOS agent files..."
echo "Placeholder macOS x64 agent archive" | gzip > "$RELEASE_DIR/malsift-agent-macos-x64.tar.gz" 2>/dev/null || \
    (echo "Placeholder macOS x64 agent archive" > "$RELEASE_DIR/malsift-agent-macos-x64.tar" && \
     gzip "$RELEASE_DIR/malsift-agent-macos-x64.tar" 2>/dev/null || echo "Note: gzip not available, created .tar file")

echo "Placeholder macOS arm64 agent archive" | gzip > "$RELEASE_DIR/malsift-agent-macos-arm64.tar.gz" 2>/dev/null || \
    (echo "Placeholder macOS arm64 agent archive" > "$RELEASE_DIR/malsift-agent-macos-arm64.tar" && \
     gzip "$RELEASE_DIR/malsift-agent-macos-arm64.tar" 2>/dev/null || echo "Note: gzip not available, created .tar file")

print_success "Placeholder files created in $RELEASE_DIR/"
echo ""
print_status "Files created:"
ls -lh "$RELEASE_DIR/" | tail -n +2
echo ""
print_warning "IMPORTANT: These are placeholder files!"
echo "When creating a GitHub release:"
echo "  1. Replace these placeholder files with actual agent binaries"
echo "  2. Upload all files from $RELEASE_DIR/ as release assets"
echo "  3. The download URLs in the web interface will work once the release is published"
echo ""
print_status "To create a GitHub release:"
echo "  1. Go to: https://github.com/malsiftcyber/MalsiftCND/releases/new"
echo "  2. Create a new tag (e.g., v1.0.0)"
echo "  3. Upload all files from $RELEASE_DIR/ as assets"
echo "  4. Publish the release"
echo ""
print_status "For the 'latest' release URL to work, tag the release as 'latest' or ensure it's the most recent release."

