#!/usr/bin/env python3
"""
Build script for MalsiftCND Discovery Agent
Creates cross-platform executables using PyInstaller
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(command, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False


def build_agent():
    """Build agent for current platform"""
    print("Building MalsiftCND Discovery Agent...")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agent_dir = project_root / "agent"
    
    if not agent_dir.exists():
        print("Error: Agent directory not found")
        return False
    
    # Install PyInstaller if not present
    print("Installing PyInstaller...")
    if not run_command(f"{sys.executable} -m pip install pyinstaller"):
        return False
    
    # Create build directory
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    build_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)
    
    # Build agent
    current_platform = platform.system().lower()
    current_arch = platform.machine().lower()
    
    print(f"Building for {current_platform} {current_arch}...")
    
    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed" if current_platform == "windows" else "--console",
        "--name", f"malsift-agent-{current_platform}-{current_arch}",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(build_dir),
        "--clean",
        str(agent_dir / "malsift_agent.py")
    ]
    
    if not run_command(" ".join(pyinstaller_cmd), cwd=project_root):
        return False
    
    # Create installer scripts
    create_installer_scripts(project_root, current_platform, current_arch)
    
    print("Build completed successfully!")
    return True


def create_installer_scripts(project_root, platform_name, architecture):
    """Create installer scripts for the platform"""
    print(f"Creating installer scripts for {platform_name}...")
    
    installers_dir = project_root / "installers"
    installers_dir.mkdir(exist_ok=True)
    
    if platform_name == "windows":
        create_windows_installer(installers_dir, architecture)
    elif platform_name == "linux":
        create_linux_installer(installers_dir, architecture)
    elif platform_name == "darwin":
        create_macos_installer(installers_dir, architecture)


def create_windows_installer(installers_dir, architecture):
    """Create Windows installer script"""
    installer_content = f"""@echo off
echo Installing MalsiftCND Discovery Agent for Windows {architecture}...

REM Create installation directory
set INSTALL_DIR=%ProgramFiles%\\MalsiftCND
mkdir "%INSTALL_DIR%" 2>nul

REM Download agent binary
echo Downloading agent binary...
curl -L -o "%INSTALL_DIR%\\malsift-agent.exe" "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-windows-{architecture}.exe"

REM Create configuration file
echo Creating configuration file...
echo {{
echo   "server_url": "https://your-malsift-server.com",
echo   "ssl_enabled": true,
echo   "heartbeat_interval": 60,
echo   "scan_enabled": true,
echo   "scan_interval_minutes": 60,
echo   "target_networks": ["192.168.0.0/16", "10.0.0.0/8"],
echo   "excluded_networks": ["127.0.0.0/8"],
echo   "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389],
echo   "log_level": "INFO"
echo }} > "%INSTALL_DIR%\\agent_config.json"

REM Install as Windows service
echo Installing as Windows service...
sc create MalsiftAgent binPath= "%INSTALL_DIR%\\malsift-agent.exe" start= auto
sc start MalsiftAgent

echo.
echo MalsiftCND Discovery Agent installed successfully!
echo Installation directory: %INSTALL_DIR%
echo The agent will start automatically on system boot.
echo.
echo To configure the agent, edit: %INSTALL_DIR%\\agent_config.json
echo To view logs, check: %INSTALL_DIR%\\malsift_agent.log
echo.
pause
"""
    
    installer_file = installers_dir / f"install-windows-{architecture}.bat"
    with open(installer_file, 'w') as f:
        f.write(installer_content)
    
    print(f"Created Windows installer: {installer_file}")


def create_linux_installer(installers_dir, architecture):
    """Create Linux installer script"""
    installer_content = f"""#!/bin/bash
echo "Installing MalsiftCND Discovery Agent for Linux {architecture}..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create installation directory
INSTALL_DIR="/opt/malsift"
mkdir -p "$INSTALL_DIR"

# Download agent binary
echo "Downloading agent binary..."
curl -L -o "$INSTALL_DIR/malsift-agent" "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-linux-{architecture}"

# Make executable
chmod +x "$INSTALL_DIR/malsift-agent"

# Create configuration file
echo "Creating configuration file..."
cat > "$INSTALL_DIR/agent_config.json" << 'EOF'
{{
  "server_url": "https://your-malsift-server.com",
  "ssl_enabled": true,
  "heartbeat_interval": 60,
  "scan_enabled": true,
  "scan_interval_minutes": 60,
  "target_networks": ["192.168.0.0/16", "10.0.0.0/8"],
  "excluded_networks": ["127.0.0.0/8"],
  "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389],
  "log_level": "INFO"
}}
EOF

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/malsift-agent.service << 'EOF'
[Unit]
Description=MalsiftCND Discovery Agent
After=network.target

[Service]
Type=simple
User=malsift
Group=malsift
WorkingDirectory=/opt/malsift
ExecStart=/opt/malsift/malsift-agent
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create user and set permissions
echo "Creating user and setting permissions..."
useradd -r -s /bin/false malsift 2>/dev/null || true
chown -R malsift:malsift "$INSTALL_DIR"

# Enable and start service
echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable malsift-agent
systemctl start malsift-agent

echo
echo "MalsiftCND Discovery Agent installed successfully!"
echo "Installation directory: $INSTALL_DIR"
echo "The agent will start automatically on system boot."
echo
echo "To configure the agent, edit: $INSTALL_DIR/agent_config.json"
echo "To view logs, use: journalctl -u malsift-agent -f"
echo "To check status, use: systemctl status malsift-agent"
echo
"""
    
    installer_file = installers_dir / f"install-linux-{architecture}.sh"
    with open(installer_file, 'w') as f:
        f.write(installer_content)
    
    # Make executable
    os.chmod(installer_file, 0o755)
    
    print(f"Created Linux installer: {installer_file}")


def create_macos_installer(installers_dir, architecture):
    """Create macOS installer script"""
    installer_content = f"""#!/bin/bash
echo "Installing MalsiftCND Discovery Agent for macOS {architecture}..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create installation directory
INSTALL_DIR="/opt/malsift"
mkdir -p "$INSTALL_DIR"

# Download agent binary
echo "Downloading agent binary..."
curl -L -o "$INSTALL_DIR/malsift-agent" "https://github.com/malsiftcyber/MalsiftCND/releases/latest/download/malsift-agent-macos-{architecture}"

# Make executable
chmod +x "$INSTALL_DIR/malsift-agent"

# Create configuration file
echo "Creating configuration file..."
cat > "$INSTALL_DIR/agent_config.json" << 'EOF'
{{
  "server_url": "https://your-malsift-server.com",
  "ssl_enabled": true,
  "heartbeat_interval": 60,
  "scan_enabled": true,
  "scan_interval_minutes": 60,
  "target_networks": ["192.168.0.0/16", "10.0.0.0/8"],
  "excluded_networks": ["127.0.0.0/8"],
  "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389],
  "log_level": "INFO"
}}
EOF

# Create launchd plist
echo "Creating launchd service..."
cat > /Library/LaunchDaemons/com.malsift.agent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.malsift.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/malsift/malsift-agent</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/malsift-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/malsift-agent.error.log</string>
</dict>
</plist>
EOF

# Set permissions
chown root:wheel /Library/LaunchDaemons/com.malsift.agent.plist
chmod 644 /Library/LaunchDaemons/com.malsift.agent.plist

# Load and start service
echo "Loading and starting service..."
launchctl load /Library/LaunchDaemons/com.malsift.agent.plist
launchctl start com.malsift.agent

echo
echo "MalsiftCND Discovery Agent installed successfully!"
echo "Installation directory: $INSTALL_DIR"
echo "The agent will start automatically on system boot."
echo
echo "To configure the agent, edit: $INSTALL_DIR/agent_config.json"
echo "To view logs, use: tail -f /var/log/malsift-agent.log"
echo "To check status, use: launchctl list | grep malsift"
echo
"""
    
    installer_file = installers_dir / f"install-macos-{architecture}.sh"
    with open(installer_file, 'w') as f:
        f.write(installer_content)
    
    # Make executable
    os.chmod(installer_file, 0o755)
    
    print(f"Created macOS installer: {installer_file}")


def main():
    """Main entry point"""
    if not build_agent():
        sys.exit(1)
    
    print("\nBuild completed successfully!")
    print("Agent binaries are in the 'dist' directory")
    print("Installer scripts are in the 'installers' directory")


if __name__ == "__main__":
    main()
