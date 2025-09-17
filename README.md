# MalsiftCND - Attack Surface Discovery Tool

A comprehensive enterprise-grade attack surface discovery tool designed for network security professionals and administrators.

## Overview

MalsiftCND is an advanced network discovery and attack surface management platform that combines traditional network scanning tools with AI-powered analysis to provide accurate device identification and comprehensive network visibility.

## Features

- **Multi-Scanner Integration**: Leverages nmap, masscan, and other proven scanning tools
- **AI-Powered Analysis**: Integrates with LLM APIs (ChatGPT, Anthropic, Grok) for enhanced device identification
- **Device Correction System**: Correct mis-identifications and improve AI accuracy over time
- **Pattern Learning**: Automatic extraction and application of identification patterns
- **CSV Export System**: Export discovery reports and device data in CSV format
- **Company & Site Tagging**: Multi-tenant data segregation with company and site management
- **EDR Integration**: Connect with CrowdStrike Falcon, Microsoft Defender, SentinelOne, and TrendMicro Vision One
- **AI-Based Accuracy Ranking**: Intelligent evaluation and ranking of data sources by accuracy and effectiveness
- **Cross-Platform Discovery Agents**: Deployable agents for Windows, Linux, and macOS with SSL-encrypted communication
- **Automated Scheduling**: Configurable discovery scan scheduling with multiple frequency options
- **New Device Detection**: Export newly discovered devices from the last 24 hours (or custom timeframe)
- **Enterprise Integrations**: Connects with RunZero, Tanium, Armis, and Active Directory/Azure AD
- **Secure Authentication**: Supports local users, AD, and Azure AD with optional MFA
- **SSL/TLS Support**: LetEncrypt and enterprise certificate support
- **REST API**: Full API for automation tool integration
- **Admin Interface**: Comprehensive configuration, throttling, and scheduling controls

## Quick Start

### Ubuntu 24.04 LTS Installation

**Prerequisites Installation**:

**Option 1: Direct Download (Recommended)**:
```bash
# Download and run the installation script
wget https://raw.githubusercontent.com/malsiftcyber/MalsiftCND/main/scripts/install-prerequisites-ubuntu.sh
chmod +x install-prerequisites-ubuntu.sh
./install-prerequisites-ubuntu.sh
```

**Option 2: Clone Repository First**:
```bash
# Clone the repository first
git clone https://github.com/malsiftcyber/MalsiftCND.git
cd MalsiftCND

# Run the installation script
./scripts/install-prerequisites-ubuntu.sh
```

**Option 3: Simple Installation (No PPA)**:
```bash
# Download and run the simple installation script (uses system Python 3.12)
wget https://raw.githubusercontent.com/malsiftcyber/MalsiftCND/main/scripts/install-prerequisites-ubuntu-simple.sh
chmod +x install-prerequisites-ubuntu-simple.sh
./install-prerequisites-ubuntu-simple.sh
```

**Option 4: Manual Installation**:
Follow the detailed instructions in the [Installation Guide](docs/installation.md)

**MalsiftCND Installation**:
```bash
# Clone repository
git clone https://github.com/malsiftcyber/MalsiftCND.git
cd MalsiftCND

# Configure environment
cp env.example .env
nano .env  # Edit configuration

# Start with Docker
docker compose up -d
```

### Other Platforms

1. [Installation Guide](docs/installation.md)
2. [Quick Start Guide](docs/quickstart.md)
3. [Configuration](docs/configuration.md)

## Documentation

- [Enterprise Deployment Guide](docs/enterprise-deployment.md)
- [Installation Guide](docs/installation.md)
- [Quick Start Guide](docs/quickstart.md)
- [Admin Manual](docs/admin-manual.md)
- [API Reference](docs/api-reference.md)
- [User Manual](docs/user-manual.md)

## Architecture

The system consists of several key components:

- **Core Scanner Engine**: Handles network discovery and port scanning
- **AI Analysis Module**: Processes scan results through LLM APIs
- **Data Aggregation Layer**: Combines and correlates data from multiple sources
- **Integration Hub**: Manages connections to external security tools
- **Web Interface**: Provides admin and user interfaces
- **API Gateway**: Exposes RESTful endpoints for automation

## Security

- All communications encrypted with TLS
- Role-based access control
- Optional multi-factor authentication
- Secure credential storage
- Audit logging

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For enterprise support and questions, please contact: support@malsift.com
