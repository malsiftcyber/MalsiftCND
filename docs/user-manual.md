# User Manual

This manual provides guidance for users of MalsiftCND, covering common tasks and features.

## Getting Started

### First Login

1. **Access the Web Interface:**
   - Open your browser
   - Navigate to `https://malsift.yourcompany.com`
   - Enter your username and password
   - Click "Login"

2. **Complete Profile Setup:**
   - Update your profile information
   - Set up two-factor authentication (recommended)
   - Configure notification preferences

3. **Familiarize Yourself with the Interface:**
   - Dashboard overview
   - Navigation menu
   - User profile settings

### Dashboard Overview

The dashboard provides a high-level view of your network security posture:

**Key Metrics:**
- Total devices discovered
- Active scans running
- Recent discoveries
- Risk score distribution

**Quick Actions:**
- Start new scan
- View recent results
- Access device inventory
- Generate reports

## Scanning

### Creating Scans

#### Basic Scan Configuration

1. **Navigate to Scans → New Scan**
2. **Configure Target Selection:**
   - Enter IP addresses: `192.168.1.1`
   - Enter IP ranges: `192.168.1.0/24`
   - Enter hostnames: `server.company.com`
   - Upload target list from file

3. **Select Scan Type:**
   - **Ping Sweep**: Quick network discovery
   - **Port Scan**: Comprehensive port discovery
   - **Service Detection**: Identify running services
   - **OS Detection**: Determine operating systems
   - **Vulnerability Scan**: Security assessment

4. **Choose Scanner:**
   - **Nmap**: Detailed, accurate results
   - **Masscan**: High-speed port scanning

5. **Configure Advanced Options:**
   - **Ports**: Specific ports or ranges
   - **Timeout**: Scan duration limit
   - **Rate Limit**: Network impact control

#### Scan Examples

**Network Discovery:**
```
Targets: 192.168.1.0/24
Scan Type: Ping Sweep
Scanner: Nmap
Timeout: 60 seconds
```

**Service Inventory:**
```
Targets: 10.0.0.0/8
Scan Type: Service Detection
Scanner: Nmap
Ports: 1-65535
Timeout: 300 seconds
```

**High-Speed Port Scan:**
```
Targets: 172.16.0.0/16
Scan Type: Port Scan
Scanner: Masscan
Rate Limit: 1000 packets/second
Timeout: 180 seconds
```

### Monitoring Scans

#### Real-Time Progress

**Scan Status Indicators:**
- 🟡 **Queued**: Waiting to start
- 🔵 **Running**: Currently executing
- 🟢 **Completed**: Successfully finished
- 🔴 **Failed**: Encountered errors
- ⚫ **Cancelled**: Manually stopped

**Progress Tracking:**
- Current target being scanned
- Percentage complete
- Estimated time remaining
- Results count

#### Scan Results

**Viewing Results:**
1. Click on completed scan
2. Review discovered hosts
3. Examine service details
4. Check AI analysis

**Result Details:**
- Host information (IP, hostname)
- Open ports and services
- Operating system detection
- AI-powered device identification

### Best Practices

**Scanning Guidelines:**
- Start with small network ranges
- Use appropriate scan types
- Respect network resources
- Schedule scans during off-peak hours

**Performance Tips:**
- Use Masscan for large networks
- Use Nmap for detailed analysis
- Adjust rate limits based on network capacity
- Monitor system resources

## Device Management

### Device Inventory

#### Viewing Devices

**Device List View:**
- Sort by IP address, hostname, or last seen
- Filter by device type or operating system
- Search by IP, hostname, or tags
- Export device data

**Device Details:**
- Basic information (IP, hostname, type)
- Operating system details
- Service inventory
- AI analysis results
- Discovery history

#### Device Information

**Basic Details:**
- IP address and hostname
- Device type and operating system
- Confidence score (0-100%)
- Risk score (0-10)
- First and last seen timestamps

**Service Information:**
- Open ports and protocols
- Service names and versions
- Product information
- CPE identifiers

**AI Analysis:**
- Device type identification
- Operating system detection
- Confidence assessment
- Reasoning explanation

### Organizing Devices

#### Tags and Categories

**Adding Tags:**
1. Select device(s)
2. Click "Edit Tags"
3. Add relevant tags:
   - `critical`: Important systems
   - `dmz`: DMZ devices
   - `internal`: Internal network
   - `iot`: IoT devices
   - `server`: Server systems

**Tag Management:**
- Create custom tags
- Apply bulk tag operations
- Filter by tags
- Generate tag-based reports

#### Notes and Documentation

**Adding Notes:**
1. Click on device
2. Navigate to "Notes" tab
3. Add descriptive information:
   - System purpose
   - Owner information
   - Special configurations
   - Security considerations

**Documentation Best Practices:**
- Keep notes current
- Include contact information
- Document special configurations
- Note security requirements

### Device Search and Filtering

#### Advanced Search

**Search Options:**
- IP address or range
- Hostname patterns
- Device type
- Operating system
- Tags
- Risk score range
- Discovery date range

**Search Examples:**
```
IP Range: 192.168.1.0/24
Device Type: Server
OS: Windows
Tags: critical, production
Risk Score: 5-10
```

#### Filtering Results

**Quick Filters:**
- Recently discovered (last 24 hours)
- High-risk devices (risk score > 7)
- Unknown devices (confidence < 50%)
- Critical systems (tagged as critical)

**Custom Filters:**
- Save frequently used filters
- Share filters with team members
- Export filtered results

## Reports and Analytics

### Generating Reports

#### Standard Reports

**Device Inventory Report:**
- Complete device list
- Service inventory
- Operating system distribution
- Risk assessment summary

**Scan Summary Report:**
- Scan execution details
- Discovery statistics
- Performance metrics
- Error analysis

**Security Assessment Report:**
- Risk score distribution
- Vulnerable services
- Compliance status
- Recommendations

#### Custom Reports

**Report Builder:**
1. Select report type
2. Choose data sources
3. Configure filters
4. Select output format
5. Schedule delivery

**Report Formats:**
- PDF (formatted reports)
- Excel (data analysis)
- CSV (data import)
- JSON (API integration)

### Analytics Dashboard

#### Key Metrics

**Discovery Metrics:**
- Total devices discovered
- New devices (last 30 days)
- Device type distribution
- Operating system breakdown

**Security Metrics:**
- Average risk score
- High-risk device count
- Vulnerable service count
- Compliance percentage

**Performance Metrics:**
- Scan success rate
- Average scan duration
- Resource utilization
- Error frequency

#### Trend Analysis

**Historical Data:**
- Device discovery trends
- Risk score changes
- Service changes over time
- Network growth patterns

**Comparative Analysis:**
- Month-over-month changes
- Quarter-over-quarter trends
- Year-over-year comparisons
- Benchmark comparisons

## Integrations

### External Data Sources

#### RunZero Integration

**Benefits:**
- Enhanced device identification
- Asset management data
- Vulnerability information
- Compliance status

**Configuration:**
1. Navigate to Integrations → RunZero
2. Enter API credentials
3. Configure sync settings
4. Enable auto-sync

**Data Enrichment:**
- Device type validation
- Asset ownership information
- Vulnerability data
- Compliance status

#### Active Directory Integration

**Benefits:**
- User and computer accounts
- Organizational structure
- Group memberships
- Security policies

**Configuration:**
1. Navigate to Integrations → Active Directory
2. Enter LDAP connection details
3. Configure search parameters
4. Test connection

**Data Mapping:**
- Computer accounts → Devices
- User accounts → Device owners
- Groups → Device categories
- OUs → Device locations

### API Integration

#### API Access

**Getting API Token:**
1. Navigate to Profile → API Access
2. Click "Generate Token"
3. Copy token securely
4. Set expiration date

**Using API:**
```bash
# Example API call
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://malsift.company.com/api/v1/devices/"
```

#### Automation Examples

**Scheduled Scanning:**
```python
import requests
import schedule
import time

def run_network_scan():
    response = requests.post(
        "https://malsift.company.com/api/v1/scans/",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "targets": ["192.168.1.0/24"],
            "scan_type": "port_scan"
        }
    )
    print(f"Scan started: {response.json()['scan_id']}")

# Schedule daily scans
schedule.every().day.at("02:00").do(run_network_scan)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Device Monitoring:**
```python
import requests

def check_new_devices():
    response = requests.get(
        "https://malsift.company.com/api/v1/devices/",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        params={"first_seen": "2024-01-01"}
    )
    
    new_devices = response.json()
    if new_devices:
        send_alert(f"Found {len(new_devices)} new devices")

check_new_devices()
```

## Security Features

### Multi-Factor Authentication

#### Setting Up MFA

**Using Authenticator App:**
1. Navigate to Profile → Security
2. Click "Enable Two-Factor Authentication"
3. Scan QR code with authenticator app
4. Enter verification code
5. Save backup codes

**Supported Apps:**
- Google Authenticator
- Microsoft Authenticator
- Authy
- 1Password

#### MFA Best Practices

**Security Tips:**
- Use a dedicated authenticator app
- Store backup codes securely
- Enable MFA on all accounts
- Regularly review MFA settings

**Recovery Procedures:**
- Use backup codes for account recovery
- Contact administrator for assistance
- Follow company security procedures

### Access Control

#### User Permissions

**Permission Levels:**
- **Viewer**: Read-only access
- **Operator**: Scan and view permissions
- **Admin**: Full system access

**Feature Access:**
- Device viewing and search
- Scan creation and management
- Report generation
- User management (admin only)
- System configuration (admin only)

#### Security Policies

**Password Requirements:**
- Minimum 12 characters
- Mixed case, numbers, symbols
- No dictionary words
- No personal information

**Session Management:**
- 30-minute timeout
- Automatic logout on inactivity
- Concurrent session limits
- IP address restrictions

## Troubleshooting

### Common Issues

#### Login Problems

**Forgotten Password:**
1. Click "Forgot Password" on login page
2. Enter email address
3. Check email for reset link
4. Follow instructions to reset

**Account Locked:**
1. Contact administrator
2. Provide user information
3. Follow unlock procedures
4. Update password if required

#### Scan Issues

**Scan Not Starting:**
1. Check target format (valid IPs/CIDR)
2. Verify network connectivity
3. Review scan queue status
4. Contact administrator if needed

**Scan Taking Too Long:**
1. Check target count and complexity
2. Review network conditions
3. Adjust timeout settings
4. Consider using faster scanner

#### Performance Issues

**Slow Interface:**
1. Check internet connection
2. Clear browser cache
3. Try different browser
4. Contact support if persistent

**Data Not Loading:**
1. Refresh page
2. Check browser console for errors
3. Verify API connectivity
4. Contact administrator

### Getting Help

#### Support Channels

**Internal Support:**
- IT Help Desk: helpdesk@company.com
- Security Team: security@company.com
- System Administrator: admin@company.com

**External Support:**
- Malsift Support: support@malsift.com
- Documentation: This manual
- Community Forum: GitHub Discussions

#### Reporting Issues

**Bug Reports:**
1. Document the issue clearly
2. Include steps to reproduce
3. Provide error messages
4. Include system information

**Feature Requests:**
1. Describe the desired functionality
2. Explain the business case
3. Provide use case examples
4. Submit through appropriate channel

#### Training Resources

**Documentation:**
- User Manual (this document)
- API Reference
- Admin Manual
- Installation Guide

**Training Materials:**
- Video tutorials
- Webinar recordings
- Best practices guides
- Case studies
