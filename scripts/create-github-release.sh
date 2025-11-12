#!/bin/bash
# Script to create a GitHub release with agent files
# This automates the release creation process

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

# Configuration
REPO="malsiftcyber/MalsiftCND"
RELEASE_DIR="release-assets"

# Check if GitHub CLI is installed
if command -v gh >/dev/null 2>&1; then
    print_success "GitHub CLI (gh) is installed"
    USE_GH_CLI=true
elif [ -n "$GITHUB_TOKEN" ]; then
    print_status "Using GitHub API with GITHUB_TOKEN"
    USE_GH_CLI=false
else
    print_error "GitHub CLI (gh) is not installed and GITHUB_TOKEN is not set"
    echo ""
    echo "Please either:"
    echo "  1. Install GitHub CLI: https://cli.github.com/"
    echo "     Then run: gh auth login"
    echo "  OR"
    echo "  2. Set GITHUB_TOKEN environment variable with a GitHub personal access token"
    echo "     Token needs 'repo' scope"
    exit 1
fi

# Check if release assets directory exists
if [ ! -d "$RELEASE_DIR" ]; then
    print_warning "Release assets directory not found. Creating placeholder files..."
    if [ -f "scripts/create-agent-release-files.sh" ]; then
        bash scripts/create-agent-release-files.sh
    else
        print_error "Cannot find scripts/create-agent-release-files.sh"
        exit 1
    fi
fi

# Check if files exist
if [ ! -f "$RELEASE_DIR/malsift-agent-windows-x64.exe" ]; then
    print_warning "Agent files not found in $RELEASE_DIR/"
    print_status "These should be actual agent binaries, not placeholders"
    read -p "Continue with placeholder files? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborted. Please add actual agent binaries to $RELEASE_DIR/ and try again"
        exit 1
    fi
fi

# Get release version
read -p "Enter release version/tag (e.g., v1.0.0): " RELEASE_TAG
if [ -z "$RELEASE_TAG" ]; then
    print_error "Release tag is required"
    exit 1
fi

# Get release title
read -p "Enter release title (press Enter for '$RELEASE_TAG'): " RELEASE_TITLE
RELEASE_TITLE=${RELEASE_TITLE:-$RELEASE_TAG}

# Get release notes
print_status "Enter release notes (press Ctrl+D when done, or leave empty):"
RELEASE_NOTES=$(cat 2>/dev/null || echo "")

# Create release using GitHub CLI
if [ "$USE_GH_CLI" = true ]; then
    print_status "Creating GitHub release using GitHub CLI..."
    
    # Create release
    if [ -n "$RELEASE_NOTES" ]; then
        gh release create "$RELEASE_TAG" \
            --title "$RELEASE_TITLE" \
            --notes "$RELEASE_NOTES" \
            "$RELEASE_DIR"/* \
            --repo "$REPO"
    else
        gh release create "$RELEASE_TAG" \
            --title "$RELEASE_TITLE" \
            --notes "Agent release $RELEASE_TAG" \
            "$RELEASE_DIR"/* \
            --repo "$REPO"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Release created successfully!"
        print_status "Release URL: https://github.com/$REPO/releases/tag/$RELEASE_TAG"
        print_status "Download URLs will work once the release is published"
    else
        print_error "Failed to create release"
        exit 1
    fi

# Create release using GitHub API
else
    print_status "Creating GitHub release using GitHub API..."
    
    # Create release via API
    RELEASE_RESPONSE=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$REPO/releases" \
        -d "{
            \"tag_name\": \"$RELEASE_TAG\",
            \"name\": \"$RELEASE_TITLE\",
            \"body\": $(echo "$RELEASE_NOTES" | jq -Rs .),
            \"draft\": false,
            \"prerelease\": false
        }")
    
    # Check if release was created
    RELEASE_ID=$(echo "$RELEASE_RESPONSE" | jq -r '.id // empty')
    if [ -z "$RELEASE_ID" ] || [ "$RELEASE_ID" = "null" ]; then
        print_error "Failed to create release"
        echo "$RELEASE_RESPONSE" | jq '.' 2>/dev/null || echo "$RELEASE_RESPONSE"
        exit 1
    fi
    
    print_success "Release created (ID: $RELEASE_ID)"
    
    # Upload assets
    print_status "Uploading release assets..."
    for file in "$RELEASE_DIR"/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            print_status "Uploading $filename..."
            
            UPLOAD_RESPONSE=$(curl -s -X POST \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Accept: application/vnd.github.v3+json" \
                -H "Content-Type: application/octet-stream" \
                --data-binary "@$file" \
                "https://uploads.github.com/repos/$REPO/releases/$RELEASE_ID/assets?name=$filename")
            
            if echo "$UPLOAD_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
                print_success "Uploaded $filename"
            else
                print_warning "Failed to upload $filename"
                echo "$UPLOAD_RESPONSE" | jq '.' 2>/dev/null || echo "$UPLOAD_RESPONSE"
            fi
        fi
    done
    
    print_success "Release created successfully!"
    print_status "Release URL: https://github.com/$REPO/releases/tag/$RELEASE_TAG"
fi

echo ""
print_success "Release creation complete!"
print_status "The download links in the web interface should now work."
print_status "If this is your latest release, the '/latest/download/' URLs will work automatically."

