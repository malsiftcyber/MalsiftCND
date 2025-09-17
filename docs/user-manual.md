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

### Correcting Device Identifications

#### Device Correction Interface

**Accessing Corrections:**
1. Navigate to device details
2. Click "Correct Identification" button
3. Review current AI analysis
4. Provide corrected information

**Correction Process:**
1. **Select Correct Device Type**: Choose from predefined categories
2. **Specify Operating System**: Enter accurate OS information
3. **Provide Reason**: Explain why the correction is needed
4. **Add Tags**: Include relevant tags for better organization
5. **Submit Correction**: Apply the correction to improve future identifications

**Correction Benefits:**
- Improves AI accuracy over time
- Creates learning patterns for similar devices
- Maintains correction history for audit purposes
- Enables verification by administrators

#### AI Pattern Learning

**Automatic Pattern Extraction:**
- Service patterns: Common service combinations
- Banner patterns: Specific service banners
- Port patterns: Typical port configurations

**Pattern Application:**
- Automatic suggestions for new devices
- Confidence scoring for pattern matches
- Continuous learning from corrections
- Pattern verification system

#### Feedback System

**Providing Feedback:**
1. Rate identification accuracy (0-100%)
2. Specify which aspects were accurate:
   - Device type identification
   - Operating system detection
   - Service identification
3. Add comments and suggestions
4. Submit feedback for system improvement

**Feedback Types:**
- **Accurate**: Identification was correct
- **Inaccurate**: Significant errors in identification
- **Partially Accurate**: Some aspects correct, others incorrect

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

## Company & Site Management

### Multi-Tenant Data Segregation

**Company Management:**
MalsiftCND supports multi-tenant deployments where different companies or business units can be segregated using company and site tagging.

**Company Features:**
- **Company Creation**: Create companies with unique names and codes
- **Contact Information**: Store company contact details and addresses
- **Site Management**: Create multiple sites within each company
- **Data Segregation**: All devices and scans are tagged with company/site information
- **Export Filtering**: Export reports filtered by company or site

**Site Management:**
- **Site Creation**: Create sites within companies with unique codes
- **Location Information**: Store detailed address and location data
- **Timezone Support**: Configure timezone for each site
- **Device Association**: Associate devices with specific sites

### Managing Companies

**Creating Companies:**
1. Navigate to Company & Site Management
2. Click "Add Company"
3. Enter company details:
   - Company Name (e.g., "Acme Corporation")
   - Company Code (e.g., "ACME", "CORP1")
   - Description and contact information
   - Address details
4. Save the company

**Company Codes:**
- Must be unique across all companies
- Used for data segregation and filtering
- Appears in all exports and reports
- Short, memorable codes recommended

### Managing Sites

**Creating Sites:**
1. Select the parent company
2. Click "Add Site"
3. Enter site details:
   - Site Name (e.g., "Headquarters", "Branch Office 1")
   - Site Code (e.g., "HQ", "BR1", "DC1")
   - Location information
   - Timezone configuration
4. Save the site

**Site Codes:**
- Must be unique within each company
- Used for location-based data segregation
- Appears in device exports and reports
- Short, descriptive codes recommended

### Device Tagging

**Tagging Devices:**
1. Enter device IP address
2. Select company and site from dropdowns
3. Add custom tags in JSON format
4. Apply tags to the device

**Tag Types:**
- **Company Tags**: Associate device with company
- **Site Tags**: Associate device with specific site
- **Custom Tags**: Add custom key-value pairs (department, environment, etc.)

**Tag Examples:**
```json
{
  "department": "IT",
  "environment": "production",
  "owner": "john.doe@company.com",
  "criticality": "high"
}
```

### Export Integration

**Company/Site in Exports:**
All CSV exports now include:
- Company Name and Company Code columns
- Site Name and Site Code columns
- Custom tags in separate columns

**Filtered Exports:**
- Export devices by company
- Export devices by site
- Export devices by custom tag values
- Multi-company reports for MSPs

## EDR Integration

### Endpoint Detection and Response Integration

**EDR Platform Support:**
MalsiftCND integrates with leading EDR platforms to enhance device identification accuracy and provide real-time endpoint data.

**Supported EDR Platforms:**
- **CrowdStrike Falcon**: Industry-leading EDR platform
- **Microsoft Defender for Endpoint**: Microsoft's comprehensive security solution
- **SentinelOne**: Advanced endpoint protection platform
- **TrendMicro Vision One**: Extended detection and response platform

**Integration Benefits:**
- **Enhanced Accuracy**: Agent-based data provides precise device information
- **Real-time Data**: Live endpoint status and security posture
- **Threat Intelligence**: Security alerts and threat detection
- **Compliance Data**: Endpoint compliance and risk scoring
- **Network Visibility**: Network connections and communication patterns

### EDR Integration Setup

**Creating EDR Integrations:**
1. Navigate to EDR Integration Management
2. Click "Add EDR Integration"
3. Configure integration details:
   - **Integration Name**: Descriptive name for the integration
   - **EDR Provider**: Select from supported platforms
   - **API Configuration**: API URL and authentication details
   - **Sync Settings**: Configure data synchronization options

**Authentication Configuration:**
- **OAuth (CrowdStrike, Microsoft Defender)**: Client ID, Client Secret, Tenant ID
- **API Key (SentinelOne, TrendMicro)**: API key authentication
- **Bearer Token**: Token-based authentication

**Sync Configuration:**
- **Sync Endpoints**: Import device/endpoint data
- **Sync Alerts**: Import security alerts and incidents
- **Sync Vulnerabilities**: Import vulnerability data
- **Sync Network Connections**: Import network communication data
- **Sync Interval**: Configure automatic sync frequency (5-1440 minutes)

### EDR Data Integration

**Endpoint Data:**
- **Device Information**: Hostname, IP addresses, MAC addresses
- **Operating System**: OS type, version, architecture
- **Hardware Details**: Processor, memory, disk space
- **Agent Status**: Online/offline status, agent version
- **Security Posture**: Risk score, threat level, compliance status

**Alert Data:**
- **Security Alerts**: Threat detection and incident data
- **Threat Intelligence**: Threat names, types, and categories
- **Severity Levels**: Low, medium, high, critical classifications
- **Timeline Data**: Detection and resolution timestamps

**Data Normalization:**
- **Standardized Format**: Consistent data structure across platforms
- **Field Mapping**: Automatic mapping of EDR-specific fields
- **Data Enrichment**: Enhanced device information from EDR sources
- **Conflict Resolution**: Handling of conflicting data from multiple sources

### EDR Management

**Integration Testing:**
- **Connectivity Test**: Verify API connectivity and authentication
- **Data Access Test**: Confirm endpoint and alert data access
- **Sync Test**: Test data synchronization functionality

**Manual Synchronization:**
- **On-demand Sync**: Manually trigger data synchronization
- **Selective Sync**: Sync specific data types (endpoints, alerts, etc.)
- **Sync Monitoring**: Monitor sync progress and results

**Integration Monitoring:**
- **Sync Logs**: View synchronization history and status
- **Error Tracking**: Monitor sync failures and errors
- **Performance Metrics**: Track sync duration and data volumes
- **Health Status**: Monitor integration health and connectivity

### EDR Data in Exports

**Enhanced CSV Exports:**
All device exports now include EDR data:
- **EDR Provider**: Source EDR platform
- **EDR Status**: Agent status (online/offline/error)
- **EDR Risk Score**: EDR-calculated risk score
- **EDR Threat Level**: Current threat level assessment

**EDR-Specific Exports:**
- **Endpoint Export**: Complete endpoint data from EDR platforms
- **Alert Export**: Security alerts and incident data
- **Compliance Export**: Endpoint compliance and risk data
- **Network Export**: Network connection and communication data

**Data Correlation:**
- **Device Matching**: Automatic matching of EDR endpoints with discovered devices
- **Data Enrichment**: Enhanced device information from EDR sources
- **Conflict Resolution**: Handling of data conflicts between sources
- **Unified View**: Combined view of network discovery and EDR data

## Scan Scheduling

### Automated Discovery Scans

**Scheduled Scanning:**
MalsiftCND supports automated discovery scans that run on configurable schedules to continuously monitor your network for new devices and changes.

**Schedule Types:**
- **Discovery Scans**: Comprehensive network discovery scans
- **Monitoring Scans**: Lightweight monitoring of known devices
- **Compliance Scans**: Regular compliance and security assessments

**Schedule Frequencies:**
- **Hourly**: Run every hour
- **Daily**: Run once per day at specified time
- **Weekly**: Run on specified days of the week
- **Custom**: Run at custom intervals (e.g., every 6 hours)

**Default Schedules:**
- **Default Discovery Scan**: Runs every 6 hours, comprehensive network discovery
- **Default Monitoring Scan**: Runs daily at 2:00 AM, lightweight monitoring

### Managing Schedules

**Viewing Schedules:**
1. Navigate to Admin → Scheduling
2. View all configured schedules
3. See next run times and statistics

**Creating New Schedules:**
1. Click "Create New Schedule"
2. Configure schedule details:
   - Name and description
   - Schedule type (Discovery/Monitoring/Compliance)
   - Frequency and timing
   - Target networks
   - Scanner configuration
3. Save and enable the schedule

**Schedule Configuration:**
- **Target Networks**: Specify IP ranges to scan
- **Scanner Settings**: Configure nmap/masscan parameters
- **Timing**: Set start times and intervals
- **Enabled/Disabled**: Control schedule activation

**Schedule Statistics:**
- Total runs and success rate
- Last run time and next scheduled run
- Success/failure counts
- Performance metrics

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

#### CSV Export Reports

**Device Export:**
- Export all devices or specific device IDs
- Include/exclude correction history
- Include/exclude service details
- Include/exclude AI analysis data
- Customizable data fields

**Discovery Report:**
- Comprehensive device overview
- Filter by date range
- Filter by device types
- Filter by risk score range
- Include discovery metrics

**Scan Results Export:**
- Export results from specific scans
- Include target information
- Include service details
- Include OS detection results
- Include scan metadata

**Corrections Export:**
- Export device correction history
- Include original vs corrected data
- Include correction reasons
- Include verification status
- Include learning metrics

#### Export Interface

**Web-Based Export:**
1. Navigate to Export Data page
2. Select export type (Devices, Discovery Report, Scan Results, Corrections)
3. Configure export options
4. Set filters and parameters
5. Click export button
6. Download CSV file

**Quick Export Options:**
- All Devices: Complete device inventory
- High Risk Devices: Devices with risk score > 7
- Recent Discoveries: Devices discovered in last 30 days
- New Devices (24h): Devices discovered in last 24 hours
- New Devices (6h): Devices discovered in last 6 hours
- Servers Only: Windows and Linux servers
- Network Devices: Routers, switches, firewalls

**Export Features:**
- Real-time export generation
- Progress indicators
- Error handling and validation
- Automatic filename generation
- Direct download to browser

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
