# How MalsiftCND Discovery Agents Work

## Overview

MalsiftCND Discovery Agents are lightweight, cross-platform applications that run on remote systems to perform network discovery scans and report results back to the central MalsiftCND server. They enable distributed scanning across multiple locations and networks.

## Architecture

### Agent Components

1. **Agent Executable** (`agent/malsift_agent.py`)
   - Python-based agent that runs on Windows, Linux, or macOS
   - Can be installed as a service (Windows Service, systemd, launchd)
   - Lightweight and resource-efficient

2. **Configuration File** (`agent_config.json`)
   - JSON-based configuration
   - Defines server URL, scan targets, ports, intervals, etc.
   - Can be customized per deployment

3. **Communication Protocol**
   - HTTPS/SSL encrypted communication with the server
   - RESTful API endpoints for registration, heartbeats, and results
   - JWT-based authentication (when implemented)

## How Agents Work

### 1. Registration

When an agent starts, it:
- Generates or loads a unique agent ID
- Registers itself with the server via `POST /api/v1/agents/register`
- Sends platform information (OS, architecture, hostname, IP)
- Receives a unique `agent_id` from the server

### 2. Heartbeat Loop

The agent continuously:
- Sends periodic heartbeats (default: every 60 seconds) via `POST /api/v1/agents/{agent_id}/heartbeat`
- Reports system metrics (CPU, memory, disk, network usage)
- Reports scan status (active scans, queued scans, errors)
- Keeps the server informed of agent health and availability

### 3. Network Scanning

If scanning is enabled, the agent:
- Performs periodic network discovery scans (default: every 60 minutes)
- Scans configured target networks (e.g., `192.168.0.0/16`, `10.0.0.0/8`)
- Uses available tools (nmap preferred, fallback to custom methods)
- Performs ping sweeps to find alive hosts
- Performs port scans on discovered hosts
- Detects services and operating systems

### 4. Results Submission

After each scan:
- Submits scan results via `POST /api/v1/agents/{agent_id}/scan-results`
- Includes discovered devices, open ports, services
- Reports scan metadata (duration, targets, scanner used)
- Handles errors gracefully and reports failures

## Agent Configuration

Example `agent_config.json`:

```json
{
  "server_url": "https://your-malsift-server.com",
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
```

## Installation

### Windows
1. Download the agent executable or installer
2. Run installer as Administrator
3. Configure `agent_config.json` with your server URL
4. Install as Windows Service (optional): `python malsift_agent.py --install-service`
5. Service starts automatically on boot

### Linux
1. Download the agent installer script
2. Run with sudo: `sudo ./install-agent.sh`
3. Configure `/opt/malsift/agent_config.json`
4. Agent runs as systemd service: `systemctl start malsift-agent`

### macOS
1. Download the agent installer script
2. Run with sudo: `sudo ./install-agent.sh`
3. Configure agent configuration file
4. Agent runs as launchd service

## Server-Side Management

The server provides endpoints to:
- **List agents**: `GET /api/v1/agents` - View all registered agents
- **Get agent status**: `GET /api/v1/agents/{agent_id}/status` - View agent health and metrics
- **Get agent scans**: `GET /api/v1/agents/{agent_id}/scans` - View scans performed by agent
- **Get agent heartbeats**: `GET /api/v1/agents/{agent_id}/heartbeats` - View heartbeat history
- **Check for updates**: `GET /api/v1/agents/{agent_id}/updates` - Check if agent needs updating
- **Delete agent**: `DELETE /api/v1/agents/{agent_id}` - Remove agent from system

## Benefits

1. **Distributed Scanning**: Scan multiple networks from different locations
2. **Reduced Server Load**: Scans run locally on agents
3. **Network Segmentation**: Agents can scan networks the server can't reach
4. **Continuous Monitoring**: Agents run 24/7, performing periodic scans
5. **Scalability**: Add more agents to increase scanning capacity

## Security

- **SSL/TLS Encryption**: All communication encrypted
- **Agent Authentication**: Unique agent IDs prevent unauthorized access
- **API Key Support**: Optional API key authentication
- **Certificate Validation**: Can be configured for production (currently disabled for dev)

## Monitoring

Agents report:
- System metrics (CPU, memory, disk, network)
- Scan statistics (active, queued, completed, failed)
- Error counts and last error messages
- Uptime and agent version

This information is visible in the web interface under the "Agents" page.

