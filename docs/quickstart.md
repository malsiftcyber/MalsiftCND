# Quick Start Guide

Get up and running with MalsiftCND in minutes!

## Prerequisites

- MalsiftCND installed and running
- Admin user account created
- Network access to scan targets

## Step 1: Access the Web Interface

1. Open your browser and navigate to:
   - `http://localhost:8000` (local installation)
   - `https://your-domain.com` (production installation)

2. Login with your admin credentials

## Step 2: Configure Basic Settings

1. **Navigate to Admin → System Configuration**
2. **Set scanning parameters**:
   - Scan timeout: 300 seconds
   - Max concurrent scans: 10
   - Scan throttle rate: 100 requests/second

3. **Configure scanners**:
   - Enable nmap scanner
   - Enable masscan scanner
   - Set appropriate timeouts

## Step 3: Create Your First Scan

1. **Navigate to Scans → New Scan**
2. **Configure scan parameters**:
   - **Targets**: Enter IP addresses or CIDR blocks (e.g., `192.168.1.0/24`)
   - **Scan Type**: Select "Port Scan" for comprehensive discovery
   - **Scanner**: Choose "nmap" for detailed results
   - **Ports**: Leave empty for full port scan, or specify ranges like `1-1000`

3. **Click "Start Scan"**

## Step 4: Monitor Scan Progress

1. **View scan status** in the Scans dashboard
2. **Monitor progress** in real-time
3. **Review results** as they become available

## Step 5: Analyze Results

1. **Navigate to Devices** to see discovered devices
2. **Review AI analysis** for device identification
3. **Check confidence scores** for accuracy assessment
4. **Add tags and notes** for organization

## Step 6: Configure Integrations (Optional)

1. **Navigate to Integrations**
2. **Configure external tools**:
   - RunZero API integration
   - Tanium integration
   - Active Directory connection
   - Azure AD connection

3. **Enable auto-sync** for continuous updates

## Step 7: Set Up Authentication

1. **Configure authentication methods**:
   - Local user management
   - Active Directory integration
   - Azure AD integration

2. **Enable MFA** (recommended):
   - Navigate to your profile
   - Enable two-factor authentication
   - Scan QR code with authenticator app

## Step 8: API Integration

1. **Generate API token**:
   - Navigate to your profile
   - Generate API access token
   - Save token securely

2. **Test API access**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/devices/
   ```

## Best Practices

### Scanning
- Start with small network ranges
- Use appropriate scan types for your needs
- Respect network resources with throttling
- Schedule scans during off-peak hours

### Security
- Use strong passwords
- Enable MFA for all users
- Regularly rotate API tokens
- Monitor access logs

### Performance
- Adjust concurrent scan limits based on network capacity
- Use masscan for high-speed port discovery
- Use nmap for detailed service detection
- Monitor system resources during scans

## Common Use Cases

### Network Discovery
1. **Initial Assessment**: Scan entire network ranges
2. **Asset Inventory**: Identify all devices and services
3. **Change Detection**: Regular scans to detect new devices
4. **Compliance**: Verify network security posture

### Security Analysis
1. **Vulnerability Assessment**: Identify exposed services
2. **Attack Surface Mapping**: Understand potential entry points
3. **Threat Intelligence**: Correlate with external data sources
4. **Incident Response**: Rapid network reconnaissance

### Automation
1. **CI/CD Integration**: Automated security testing
2. **Monitoring**: Continuous network monitoring
3. **Reporting**: Automated security reports
4. **Alerting**: Notifications for new devices

## Next Steps

- [Configuration Guide](configuration.md) - Advanced configuration options
- [Enterprise Deployment](enterprise-deployment.md) - Production deployment
- [API Reference](api-reference.md) - Programmatic access
- [Admin Manual](admin-manual.md) - System administration

## Getting Help

- **Documentation**: This site
- **Support**: support@malsift.com
- **Community**: GitHub Discussions
- **Issues**: GitHub Issues
