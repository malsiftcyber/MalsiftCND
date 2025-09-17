# MalsiftCND Discovery Agent PowerShell Installer
# Run as Administrator

param(
    [string]$ServerUrl = "https://your-malsift-server.com",
    [string]$InstallPath = "$env:ProgramFiles\MalsiftCND",
    [switch]$SkipService,
    [switch]$Uninstall
)

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

if ($Uninstall) {
    Write-Host "Uninstalling MalsiftCND Discovery Agent..." -ForegroundColor Yellow
    
    # Stop and remove service
    try {
        Stop-Service -Name "MalsiftCND Agent" -Force -ErrorAction SilentlyContinue
        Remove-Service -Name "MalsiftCND Agent" -ErrorAction SilentlyContinue
        Write-Host "Service removed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Service removal failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Remove files
    if (Test-Path $InstallPath) {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Host "Files removed successfully" -ForegroundColor Green
    }
    
    # Remove Start Menu shortcuts
    $StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MalsiftCND"
    if (Test-Path $StartMenuPath) {
        Remove-Item -Path $StartMenuPath -Recurse -Force
        Write-Host "Start Menu shortcuts removed" -ForegroundColor Green
    }
    
    # Remove Desktop shortcut
    $DesktopShortcut = "$env:USERPROFILE\Desktop\MalsiftCND Agent.lnk"
    if (Test-Path $DesktopShortcut) {
        Remove-Item -Path $DesktopShortcut -Force
        Write-Host "Desktop shortcut removed" -ForegroundColor Green
    }
    
    Write-Host "MalsiftCND Discovery Agent uninstalled successfully!" -ForegroundColor Green
    exit 0
}

Write-Host "Installing MalsiftCND Discovery Agent..." -ForegroundColor Yellow
Write-Host "Server URL: $ServerUrl" -ForegroundColor Cyan
Write-Host "Install Path: $InstallPath" -ForegroundColor Cyan

# Create installation directory
if (-not (Test-Path $InstallPath)) {
    New-Item -Path $InstallPath -ItemType Directory -Force | Out-Null
    Write-Host "Created installation directory: $InstallPath" -ForegroundColor Green
}

# Create logs directory
$LogsPath = "$InstallPath\logs"
if (-not (Test-Path $LogsPath)) {
    New-Item -Path $LogsPath -ItemType Directory -Force | Out-Null
    Write-Host "Created logs directory: $LogsPath" -ForegroundColor Green
}

# Create configuration file
$ConfigContent = @"
{
  "server_url": "$ServerUrl",
  "ssl_enabled": true,
  "heartbeat_interval": 60,
  "scan_enabled": true,
  "scan_interval_minutes": 60,
  "max_concurrent_scans": 5,
  "scan_timeout_seconds": 300,
  "target_networks": ["192.168.0.0/16", "10.0.0.0/8"],
  "excluded_networks": ["127.0.0.0/8"],
  "target_ports": [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389],
  "excluded_ports": [],
  "log_level": "INFO",
  "log_file": "malsift_agent.log"
}
"@

$ConfigPath = "$InstallPath\agent_config.json"
Set-Content -Path $ConfigPath -Value $ConfigContent -Encoding UTF8
Write-Host "Created configuration file: $ConfigPath" -ForegroundColor Green

# Create README file
$ReadmeContent = @"
MalsiftCND Discovery Agent

This is the MalsiftCND Discovery Agent for Windows.

Installation:
- Installed as Windows Service
- Configuration: agent_config.json
- Logs: logs\ directory

Configuration:
Edit agent_config.json to configure the agent settings.

Service Management:
- Start: Start-Service "MalsiftCND Agent"
- Stop: Stop-Service "MalsiftCND Agent"
- Status: Get-Service "MalsiftCND Agent"

Documentation:
https://github.com/malsiftcyber/MalsiftCND

Support:
https://github.com/malsiftcyber/MalsiftCND/issues
"@

$ReadmePath = "$InstallPath\README.txt"
Set-Content -Path $ReadmePath -Value $ReadmeContent -Encoding UTF8
Write-Host "Created README file: $ReadmePath" -ForegroundColor Green

# Install as Windows Service (if not skipped)
if (-not $SkipService) {
    try {
        # Check if agent executable exists
        $AgentExe = "$InstallPath\malsift-agent.exe"
        if (-not (Test-Path $AgentExe)) {
            Write-Host "Agent executable not found: $AgentExe" -ForegroundColor Red
            Write-Host "Please ensure malsift-agent.exe is in the installation directory" -ForegroundColor Yellow
            exit 1
        }
        
        # Install service
        & $AgentExe --install-service
        Write-Host "Windows Service installed successfully" -ForegroundColor Green
        
        # Start service
        Start-Service -Name "MalsiftCND Agent"
        Write-Host "Windows Service started successfully" -ForegroundColor Green
        
    } catch {
        Write-Host "Service installation failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You can install the service manually later using:" -ForegroundColor Yellow
        Write-Host "  & `"$InstallPath\malsift-agent.exe`" --install-service" -ForegroundColor Yellow
    }
}

# Create Start Menu shortcuts
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MalsiftCND"
if (-not (Test-Path $StartMenuPath)) {
    New-Item -Path $StartMenuPath -ItemType Directory -Force | Out-Null
}

# Create shortcuts
$WshShell = New-Object -ComObject WScript.Shell

# Agent shortcut
$AgentShortcut = $WshShell.CreateShortcut("$StartMenuPath\MalsiftCND Agent.lnk")
$AgentShortcut.TargetPath = "$InstallPath\malsift-agent.exe"
$AgentShortcut.WorkingDirectory = $InstallPath
$AgentShortcut.Description = "MalsiftCND Discovery Agent"
$AgentShortcut.Save()

# Configuration shortcut
$ConfigShortcut = $WshShell.CreateShortcut("$StartMenuPath\Configuration.lnk")
$ConfigShortcut.TargetPath = "notepad.exe"
$ConfigShortcut.Arguments = "$InstallPath\agent_config.json"
$ConfigShortcut.Description = "Edit Agent Configuration"
$ConfigShortcut.Save()

# Uninstall shortcut
$UninstallShortcut = $WshShell.CreateShortcut("$StartMenuPath\Uninstall.lnk")
$UninstallShortcut.TargetPath = "powershell.exe"
$UninstallShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$InstallPath\uninstall-agent.ps1`""
$UninstallShortcut.Description = "Uninstall MalsiftCND Agent"
$UninstallShortcut.Save()

Write-Host "Start Menu shortcuts created" -ForegroundColor Green

# Create Desktop shortcut
$DesktopShortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\MalsiftCND Agent.lnk")
$DesktopShortcut.TargetPath = "$InstallPath\malsift-agent.exe"
$DesktopShortcut.WorkingDirectory = $InstallPath
$DesktopShortcut.Description = "MalsiftCND Discovery Agent"
$DesktopShortcut.Save()

Write-Host "Desktop shortcut created" -ForegroundColor Green

# Create uninstaller script
$UninstallScript = @"
# MalsiftCND Discovery Agent Uninstaller
# Run as Administrator

param([switch]$Force)

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

Write-Host "Uninstalling MalsiftCND Discovery Agent..." -ForegroundColor Yellow

# Stop and remove service
try {
    Stop-Service -Name "MalsiftCND Agent" -Force -ErrorAction SilentlyContinue
    Remove-Service -Name "MalsiftCND Agent" -ErrorAction SilentlyContinue
    Write-Host "Service removed successfully" -ForegroundColor Green
} catch {
    Write-Host "Service removal failed: `$(`$_.Exception.Message)" -ForegroundColor Red
}

# Remove files
`$InstallPath = "`$env:ProgramFiles\MalsiftCND"
if (Test-Path `$InstallPath) {
    Remove-Item -Path `$InstallPath -Recurse -Force
    Write-Host "Files removed successfully" -ForegroundColor Green
}

# Remove Start Menu shortcuts
`$StartMenuPath = "`$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MalsiftCND"
if (Test-Path `$StartMenuPath) {
    Remove-Item -Path `$StartMenuPath -Recurse -Force
    Write-Host "Start Menu shortcuts removed" -ForegroundColor Green
}

# Remove Desktop shortcut
`$DesktopShortcut = "`$env:USERPROFILE\Desktop\MalsiftCND Agent.lnk"
if (Test-Path `$DesktopShortcut) {
    Remove-Item -Path `$DesktopShortcut -Force
    Write-Host "Desktop shortcut removed" -ForegroundColor Green
}

Write-Host "MalsiftCND Discovery Agent uninstalled successfully!" -ForegroundColor Green
"@

$UninstallScriptPath = "$InstallPath\uninstall-agent.ps1"
Set-Content -Path $UninstallScriptPath -Value $UninstallScript -Encoding UTF8
Write-Host "Created uninstaller script: $UninstallScriptPath" -ForegroundColor Green

Write-Host ""
Write-Host "MalsiftCND Discovery Agent installed successfully!" -ForegroundColor Green
Write-Host "Installation directory: $InstallPath" -ForegroundColor Cyan
Write-Host "Configuration file: $ConfigPath" -ForegroundColor Cyan
Write-Host "Logs directory: $LogsPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
try {
    Get-Service -Name "MalsiftCND Agent" | Format-Table -AutoSize
} catch {
    Write-Host "Service not found or not running" -ForegroundColor Red
}
Write-Host ""
Write-Host "To configure the agent, edit: $ConfigPath" -ForegroundColor Yellow
Write-Host "To view logs, check: $LogsPath" -ForegroundColor Yellow
Write-Host "To uninstall, run: & `"$UninstallScriptPath`"" -ForegroundColor Yellow
