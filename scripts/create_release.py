#!/usr/bin/env python3
"""
Create a GitHub release with agent files
This script can create a release programmatically if you have a GitHub token
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    import requests
except ImportError:
    print("ERROR: requests library is required")
    print("Install it with: pip install requests")
    sys.exit(1)

REPO = "malsiftcyber/MalsiftCND"
RELEASE_DIR = Path("release-assets")


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or git config"""
    # Try environment variable first
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    
    # Try GitHub CLI
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None


def create_placeholder_files():
    """Create placeholder agent files if they don't exist"""
    RELEASE_DIR.mkdir(exist_ok=True)
    
    files_to_create = [
        "malsift-agent-windows-x86.exe",
        "malsift-agent-windows-x64.exe",
        "malsift-agent-linux-x86.tar.gz",
        "malsift-agent-linux-x64.tar.gz",
        "malsift-agent-linux-arm64.tar.gz",
        "malsift-agent-macos-x64.tar.gz",
        "malsift-agent-macos-arm64.tar.gz",
    ]
    
    created = []
    for filename in files_to_create:
        filepath = RELEASE_DIR / filename
        if not filepath.exists():
            # Create a small placeholder file
            if filename.endswith(".tar.gz"):
                # Create a minimal tar.gz
                import gzip
                with gzip.open(filepath, "wb") as f:
                    f.write(f"Placeholder {filename}\n".encode())
            else:
                filepath.write_text(f"Placeholder {filename}\n")
            created.append(filename)
    
    if created:
        print(f"Created {len(created)} placeholder files:")
        for f in created:
            print(f"  - {f}")
        print("\n⚠️  WARNING: These are placeholder files!")
        print("Replace them with actual agent binaries before creating the release.")
    else:
        print("All required files already exist in release-assets/")
    
    return len(created) > 0


def create_release_via_api(tag: str, title: str, notes: str, token: str) -> Optional[dict]:
    """Create a GitHub release using the API"""
    url = f"https://api.github.com/repos/{REPO}/releases"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "tag_name": tag,
        "name": title,
        "body": notes,
        "draft": False,
        "prerelease": False
    }
    
    print(f"Creating release '{title}' with tag '{tag}'...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        release = response.json()
        print(f"✅ Release created successfully!")
        print(f"   URL: {release['html_url']}")
        return release
    else:
        print(f"❌ Failed to create release: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def upload_asset(release_id: int, filepath: Path, token: str) -> bool:
    """Upload a file as a release asset"""
    filename = filepath.name
    url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={filename}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/octet-stream"
    }
    
    print(f"  Uploading {filename}...", end=" ", flush=True)
    
    with open(filepath, "rb") as f:
        response = requests.post(url, headers=headers, data=f)
    
    if response.status_code == 201:
        print("✅")
        return True
    else:
        print(f"❌ ({response.status_code})")
        return False


def main():
    print("=" * 60)
    print("GitHub Release Creator for MalsiftCND Agent Files")
    print("=" * 60)
    print()
    
    # Check/create placeholder files
    print("Step 1: Checking release assets...")
    has_placeholders = create_placeholder_files()
    print()
    
    if has_placeholders:
        response = input("⚠️  Placeholder files detected. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted. Please add actual agent binaries to release-assets/ and try again.")
            sys.exit(1)
    
    # Get release info
    print("\nStep 2: Release information")
    tag = input("Enter release tag (e.g., v1.0.0): ").strip()
    if not tag:
        print("❌ Release tag is required")
        sys.exit(1)
    
    title = input(f"Enter release title (default: {tag}): ").strip() or tag
    notes = input("Enter release notes (optional, press Enter to skip): ").strip() or f"Agent release {tag}"
    
    # Try to get GitHub token
    print("\nStep 3: Authentication")
    token = get_github_token()
    
    if not token:
        print("❌ No GitHub authentication found")
        print("\nTo create a release programmatically, you need:")
        print("  1. Install GitHub CLI: https://cli.github.com/")
        print("     Then run: gh auth login")
        print("  OR")
        print("  2. Set GITHUB_TOKEN environment variable")
        print("     Get a token from: https://github.com/settings/tokens")
        print("     Token needs 'repo' scope")
        print("\nAlternatively, create the release manually:")
        print(f"  1. Go to: https://github.com/{REPO}/releases/new")
        print(f"  2. Tag: {tag}")
        print(f"  3. Title: {title}")
        print(f"  4. Upload all files from: {RELEASE_DIR.absolute()}/")
        sys.exit(1)
    
    print("✅ GitHub authentication found")
    
    # Create release
    print("\nStep 4: Creating release...")
    release = create_release_via_api(tag, title, notes, token)
    
    if not release:
        sys.exit(1)
    
    # Upload assets
    print("\nStep 5: Uploading assets...")
    assets = list(RELEASE_DIR.glob("*"))
    assets = [a for a in assets if a.is_file() and not a.name.startswith(".")]
    
    uploaded = 0
    for asset in assets:
        if upload_asset(release["id"], asset, token):
            uploaded += 1
    
    print(f"\n✅ Uploaded {uploaded}/{len(assets)} assets")
    print(f"\n🎉 Release created successfully!")
    print(f"   View at: {release['html_url']}")
    print(f"\nThe download links in the web interface should now work.")


if __name__ == "__main__":
    main()

