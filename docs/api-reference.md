# API Reference

MalsiftCND provides a comprehensive REST API for programmatic access to all functionality.

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication

All API endpoints require authentication using JWT tokens.

### Getting an Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password",
    "auth_type": "local"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_info": {
    "id": "user-id",
    "username": "your-username",
    "email": "user@example.com",
    "is_active": true,
    "is_admin": false
  }
}
```

### Using Access Tokens

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     "http://localhost:8000/api/v1/devices/"
```

## Endpoints

### Authentication

#### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "auth_type": "local|ad|azure"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_info": {
    "id": "string",
    "username": "string",
    "email": "string",
    "is_active": true,
    "is_admin": false
  }
}
```

#### GET /auth/me
Get current user information.

**Response:**
```json
{
  "username": "string",
  "user_id": "string"
}
```

#### POST /auth/mfa/setup
Setup MFA for current user.

**Response:**
```json
{
  "secret": "string",
  "qr_code": "base64-encoded-image",
  "backup_codes": ["string"]
}
```

#### POST /auth/mfa/verify
Verify MFA token.

**Request Body:**
```json
{
  "token": "string"
}
```

### Scans

#### POST /scans/
Create a new scan.

**Request Body:**
```json
{
  "targets": ["192.168.1.0/24", "10.0.0.1"],
  "scan_type": "port_scan",
  "ports": [22, 80, 443],
  "scanner": "nmap",
  "timeout": 300,
  "rate_limit": 100
}
```

**Response:**
```json
{
  "scan_id": "uuid",
  "status": "queued",
  "targets": ["192.168.1.0/24"],
  "scan_type": "port_scan",
  "scanner": "nmap",
  "created_at": "2024-01-01T00:00:00Z",
  "estimated_duration": 300
}
```

#### GET /scans/{scan_id}/status
Get scan status and progress.

**Response:**
```json
{
  "scan_id": "uuid",
  "status": "running",
  "progress": 45.5,
  "current_target": "192.168.1.1",
  "results_count": 12,
  "started_at": "2024-01-01T00:00:00Z",
  "estimated_completion": "2024-01-01T00:05:00Z"
}
```

#### GET /scans/{scan_id}/results
Get scan results.

**Query Parameters:**
- `limit`: Number of results (default: 100)
- `offset`: Offset for pagination (default: 0)

**Response:**
```json
[
  {
    "scan_id": "uuid",
    "target": "192.168.1.1",
    "success": true,
    "data": {
      "hosts": {
        "192.168.1.1": {
          "ip": "192.168.1.1",
          "hostname": "router.local",
          "status": "up",
          "ports": {
            "22": {
              "port": 22,
              "state": "open",
              "service": "ssh",
              "version": "OpenSSH 8.2"
            }
          },
          "os": {
            "name": "Linux",
            "accuracy": 95
          }
        }
      }
    },
    "scan_time": 2.5,
    "completed_at": "2024-01-01T00:01:00Z"
  }
]
```

#### GET /scans/
List user's scans.

**Query Parameters:**
- `limit`: Number of scans (default: 50)
- `offset`: Offset for pagination (default: 0)
- `status_filter`: Filter by status (queued, running, completed, failed, cancelled)

#### DELETE /scans/{scan_id}
Cancel a running scan.

### Devices

#### GET /devices/
List discovered devices.

**Query Parameters:**
- `limit`: Number of devices (default: 50)
- `offset`: Offset for pagination (default: 0)
- `search`: Search term
- `device_type`: Filter by device type
- `os`: Filter by operating system

**Response:**
```json
[
  {
    "ip": "192.168.1.1",
    "hostname": "router.local",
    "device_type": "Router",
    "operating_system": "Linux",
    "confidence": 0.95,
    "last_seen": "2024-01-01T00:00:00Z",
    "first_seen": "2024-01-01T00:00:00Z",
    "tags": ["network", "critical"],
    "risk_score": 3.2,
    "services": [
      {
        "port": 22,
        "service": "ssh",
        "version": "OpenSSH 8.2"
      }
    ],
    "ai_analysis": {
      "device_type": "Router",
      "operating_system": "Linux",
      "confidence": 0.95,
      "reasoning": "SSH service detected with Linux-specific banners"
    }
  }
]
```

#### GET /devices/{device_ip}
Get device details.

#### POST /devices/search
Advanced device search.

**Request Body:**
```json
{
  "query": "router",
  "device_type": "Router",
  "operating_system": "Linux",
  "ip_range": "192.168.1.0/24",
  "tags": ["network"],
  "risk_score_min": 0,
  "risk_score_max": 5
}
```

#### PUT /devices/{device_ip}/tags
Update device tags.

**Request Body:**
```json
{
  "tags": ["network", "critical", "monitored"]
}
```

#### PUT /devices/{device_ip}/notes
Update device notes.

**Request Body:**
```json
{
  "notes": "Primary network gateway"
}
```

#### GET /devices/stats/summary
Get device statistics.

### Device Corrections

#### POST /device-corrections/{device_id}/correct
Correct device identification.

**Request Body:**
```json
{
  "corrected_device_type": "Windows Server",
  "corrected_operating_system": "Windows Server 2019",
  "correction_reason": "AI incorrectly identified as Linux due to SSH service",
  "additional_tags": ["production", "critical"]
}
```

**Response:**
```json
{
  "message": "Device correction applied successfully",
  "correction": {
    "correction_id": "uuid",
    "device_id": "uuid",
    "original": {
      "device_type": "Linux Server",
      "operating_system": "Ubuntu",
      "confidence": 0.85
    },
    "corrected": {
      "device_type": "Windows Server",
      "operating_system": "Windows Server 2019",
      "confidence": 1.0
    },
    "reason": "AI incorrectly identified as Linux due to SSH service",
    "applied_at": "2024-01-01T00:00:00Z"
  }
}
```

#### GET /device-corrections/{device_id}/corrections
Get correction history for a device.

**Response:**
```json
{
  "device_id": "uuid",
  "corrections": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "original": {
        "device_type": "Linux Server",
        "operating_system": "Ubuntu",
        "confidence": 0.85
      },
      "corrected": {
        "device_type": "Windows Server",
        "operating_system": "Windows Server 2019"
      },
      "reason": "AI incorrectly identified as Linux due to SSH service",
      "applied_at": "2024-01-01T00:00:00Z",
      "is_verified": true,
      "verified_by": "uuid"
    }
  ],
  "total_corrections": 1
}
```

#### POST /device-corrections/{device_id}/feedback
Submit feedback on device identification.

**Request Body:**
```json
{
  "feedback_type": "inaccurate",
  "accuracy_score": 0.3,
  "device_type_accurate": false,
  "os_accurate": true,
  "services_accurate": true,
  "feedback_comment": "Device type was wrong but OS detection was correct",
  "suggestions": "Consider Windows-specific banners for identification"
}
```

#### POST /device-corrections/{correction_id}/verify
Verify a device correction (admin only).

**Request Body:**
```json
{
  "feedback_score": 0.9
}
```

#### GET /device-corrections/patterns
Get learned correction patterns.

**Query Parameters:**
- `pattern_type`: Filter by pattern type (service_pattern, banner_pattern, port_pattern)
- `limit`: Number of patterns (default: 50)
- `offset`: Offset for pagination (default: 0)

**Response:**
```json
{
  "patterns": [
    {
      "id": "uuid",
      "pattern_type": "service_pattern",
      "pattern_key": "ssh",
      "pattern_value": "OpenSSH 8.2",
      "correct_device_type": "Linux Server",
      "correct_operating_system": "Ubuntu 20.04",
      "confidence_score": 0.95,
      "usage_count": 15,
      "success_rate": 0.93,
      "created_at": "2024-01-01T00:00:00Z",
      "last_used": "2024-01-15T00:00:00Z"
    }
  ],
  "total_patterns": 1,
  "limit": 50,
  "offset": 0
}
```

#### POST /device-corrections/{device_id}/apply-patterns
Apply learned patterns to improve device identification.

**Response:**
```json
{
  "device_id": "uuid",
  "applied_patterns": [
    {
      "type": "service_pattern",
      "pattern": "ssh",
      "suggested_device_type": "Linux Server",
      "suggested_os": "Ubuntu 20.04",
      "confidence": 0.95
    }
  ],
  "pattern_count": 1
}
```

#### GET /device-corrections/stats/corrections
Get correction statistics.

**Response:**
```json
{
  "total_corrections": 150,
  "verified_corrections": 120,
  "verification_rate": 0.8,
  "total_patterns": 45,
  "recent_corrections": [
    {
      "id": "uuid",
      "device_id": "uuid",
      "original_type": "Linux Server",
      "corrected_type": "Windows Server",
      "created_at": "2024-01-15T00:00:00Z",
      "is_verified": true
    }
  ]
}
```

### Exports

#### GET /exports/devices/csv
Export devices to CSV format.

**Query Parameters:**
- `device_ids`: Comma-separated device IDs (optional)
- `include_corrections`: Include correction data (default: true)
- `include_services`: Include service data (default: true)
- `include_ai_analysis`: Include AI analysis data (default: true)

**Response:** CSV file download

#### POST /exports/devices/csv
Export devices to CSV format (POST method for complex filters).

**Request Body:**
```json
{
  "device_ids": ["uuid1", "uuid2"],
  "include_corrections": true,
  "include_services": true,
  "include_ai_analysis": true
}
```

**Response:** CSV file download

#### GET /exports/scans/{scan_id}/csv
Export scan results to CSV format.

**Response:** CSV file download

#### GET /exports/corrections/csv
Export device corrections to CSV format.

**Query Parameters:**
- `device_id`: Device ID to filter corrections (optional)

**Response:** CSV file download

#### GET /exports/discovery-report/csv
Export comprehensive discovery report to CSV format.

**Query Parameters:**
- `start_date`: Start date for report (ISO format)
- `end_date`: End date for report (ISO format)
- `device_types`: Comma-separated device types
- `risk_score_min`: Minimum risk score (0.0-10.0)
- `risk_score_max`: Maximum risk score (0.0-10.0)

**Response:** CSV file download

#### POST /exports/discovery-report/csv
Export comprehensive discovery report to CSV format (POST method).

**Request Body:**
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "device_types": ["Windows Server", "Linux Server"],
  "risk_score_min": 5.0,
  "risk_score_max": 10.0
}
```

**Response:** CSV file download

#### GET /exports/new-devices/csv
Export newly discovered devices from the last N hours.

**Query Parameters:**
- `hours`: Number of hours to look back (1-168, default: 24)

**Response:** CSV file download

#### GET /exports/formats
Get available export formats and options.

**Response:**
```json
{
  "formats": [
    {
      "name": "CSV",
      "description": "Comma-separated values format",
      "media_type": "text/csv",
      "supported_data": [
        "devices",
        "scan_results",
        "corrections",
        "discovery_reports",
        "new_devices"
      ]
    }
  ],
  "device_export_options": {
    "include_corrections": "Include device correction history",
    "include_services": "Include service and port information",
    "include_ai_analysis": "Include AI analysis details"
  },
  "discovery_report_options": {
    "date_range": "Filter by discovery date range",
    "device_types": "Filter by specific device types",
    "risk_score_range": "Filter by risk score range"
  },
  "new_devices_options": {
    "hours": "Number of hours to look back for new devices (1-168)"
  }
}
```

### Tagging

#### POST /tagging/companies
Create a new company.

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "code": "ACME",
  "description": "Main company",
  "contact_email": "admin@acme.com",
  "contact_phone": "+1-555-0123",
  "address": "123 Main St, City, State 12345"
}
```

#### GET /tagging/companies
List all companies.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Acme Corporation",
    "code": "ACME",
    "description": "Main company",
    "contact_email": "admin@acme.com",
    "contact_phone": "+1-555-0123",
    "address": "123 Main St, City, State 12345",
    "is_active": true,
    "created_at": "2024-01-15T00:00:00Z",
    "sites_count": 5,
    "devices_count": 150
  }
]
```

#### GET /tagging/companies/{company_id}
Get company by ID.

#### PUT /tagging/companies/{company_id}
Update company.

#### DELETE /tagging/companies/{company_id}
Delete company (soft delete).

#### POST /tagging/sites
Create a new site.

**Request Body:**
```json
{
  "company_id": "uuid",
  "name": "Headquarters",
  "code": "HQ",
  "description": "Main office",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "postal_code": "10001",
  "timezone": "America/New_York"
}
```

#### GET /tagging/sites
List sites, optionally filtered by company.

**Query Parameters:**
- `company_id`: Filter by company ID (optional)
- `active_only`: Show only active sites (default: true)

#### GET /tagging/sites/{site_id}
Get site by ID.

#### PUT /tagging/sites/{site_id}
Update site.

#### DELETE /tagging/sites/{site_id}
Delete site (soft delete).

#### POST /tagging/devices/{device_id}/tags
Tag a device with company, site, and custom tags.

**Request Body:**
```json
{
  "company_id": "uuid",
  "site_id": "uuid",
  "custom_tags": {
    "department": "IT",
    "environment": "production",
    "owner": "john.doe@company.com"
  }
}
```

#### GET /tagging/devices/{device_id}/tags
Get all tags for a device.

**Response:**
```json
{
  "company": {
    "id": "uuid",
    "name": "Acme Corporation",
    "code": "ACME"
  },
  "site": {
    "id": "uuid",
    "name": "Headquarters",
    "code": "HQ"
  },
  "custom_tags": {
    "department": "IT",
    "environment": "production",
    "owner": "john.doe@company.com"
  }
}
```

#### POST /tagging/scans/{scan_id}/tags
Tag a scan with company, site, and custom tags.

#### GET /tagging/scans/{scan_id}/tags
Get all tags for a scan.

### Scheduling

#### GET /scheduling/schedules
List all scan schedules.

**Response:**
```json
[
  {
    "schedule_id": "uuid",
    "name": "Default Discovery Scan",
    "schedule_type": "discovery",
    "frequency": "custom",
    "target_networks": ["192.168.0.0/16"],
    "enabled": true,
    "custom_interval_hours": 6,
    "start_time": "00:00",
    "days_of_week": null,
    "scanner_config": {
      "scanner": "nmap",
      "scan_type": "discovery",
      "ports": "1-1000",
      "timing": "T4"
    },
    "last_run": "2024-01-15T06:00:00Z",
    "next_run": "2024-01-15T12:00:00Z",
    "total_runs": 150,
    "successful_runs": 145,
    "failed_runs": 5
  }
]
```

#### POST /scheduling/schedules
Create a new scan schedule.

**Request Body:**
```json
{
  "name": "Custom Discovery Scan",
  "schedule_type": "discovery",
  "frequency": "daily",
  "target_networks": ["10.0.0.0/8"],
  "enabled": true,
  "start_time": "02:00",
  "scanner_config": {
    "scanner": "nmap",
    "scan_type": "discovery",
    "ports": "1-1000",
    "timing": "T3"
  }
}
```

#### PUT /scheduling/schedules/{schedule_id}
Update an existing schedule.

#### DELETE /scheduling/schedules/{schedule_id}
Delete a schedule.

#### POST /scheduling/schedules/{schedule_id}/enable
Enable a schedule.

#### POST /scheduling/schedules/{schedule_id}/disable
Disable a schedule.

#### POST /scheduling/schedules/{schedule_id}/run-now
Run a schedule immediately.

#### GET /scheduling/schedules/stats
Get scheduling statistics.

**Response:**
```json
{
  "total_schedules": 5,
  "enabled_schedules": 3,
  "disabled_schedules": 2,
  "total_runs": 500,
  "successful_runs": 485,
  "failed_runs": 15,
  "success_rate": 0.97,
  "scheduler_running": true
}
```

#### POST /scheduling/scheduler/start
Start the scan scheduler.

#### POST /scheduling/scheduler/stop
Stop the scan scheduler.

#### GET /scheduling/scheduler/status
Get scheduler status.

### Integrations

#### GET /integrations/
List available integrations.

**Response:**
```json
[
  {
    "name": "runzero",
    "enabled": true,
    "connected": true,
    "last_sync": "2024-01-01T00:00:00Z",
    "error": null
  }
]
```

#### GET /integrations/{integration_name}/status
Get integration status.

#### PUT /integrations/{integration_name}/config
Update integration configuration.

**Request Body:**
```json
{
  "name": "runzero",
  "enabled": true,
  "config": {
    "api_key": "your-api-key",
    "base_url": "https://api.runzero.com/v1.0"
  }
}
```

#### POST /integrations/{integration_name}/sync
Trigger integration sync.

**Request Body:**
```json
{
  "integration_name": "runzero",
  "force_full_sync": false
}
```

### Admin

#### GET /admin/system/config
Get system configuration.

**Response:**
```json
{
  "scan_timeout": 300,
  "max_concurrent_scans": 10,
  "scan_throttle_rate": 100,
  "ai_analysis_enabled": true,
  "auto_sync_enabled": false,
  "sync_interval": 3600
}
```

#### PUT /admin/system/config
Update system configuration.

#### GET /admin/scanners
List scanner configurations.

#### PUT /admin/scanners/{scanner_name}
Update scanner configuration.

#### GET /admin/users
List system users.

#### POST /admin/users
Create new user.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure-password",
  "is_admin": false
}
```

#### PUT /admin/users/{user_id}
Update user.

#### DELETE /admin/users/{user_id}
Delete user.

#### GET /admin/system/stats
Get system statistics.

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses include details:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Authentication**: 10 login attempts per minute per IP
- **Scans**: Configurable per user/admin settings

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

MalsiftCND supports webhooks for real-time notifications:

### Configure Webhook

```bash
curl -X POST "http://localhost:8000/api/v1/admin/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["scan.completed", "device.discovered"],
    "secret": "webhook-secret"
  }'
```

### Webhook Payload

```json
{
  "event": "scan.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "scan_id": "uuid",
    "status": "completed",
    "results_count": 25
  }
}
```

## SDKs and Examples

### Python SDK Example

```python
import requests

class MalsiftClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def create_scan(self, targets, scan_type="port_scan"):
        response = requests.post(
            f"{self.base_url}/scans/",
            json={
                "targets": targets,
                "scan_type": scan_type
            },
            headers=self.headers
        )
        return response.json()
    
    def get_devices(self):
        response = requests.get(
            f"{self.base_url}/devices/",
            headers=self.headers
        )
        return response.json()

# Usage
client = MalsiftClient("http://localhost:8000/api/v1", "your-token")
scan = client.create_scan(["192.168.1.0/24"])
devices = client.get_devices()
```

### JavaScript Example

```javascript
class MalsiftClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createScan(targets, scanType = 'port_scan') {
        const response = await fetch(`${this.baseUrl}/scans/`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                targets,
                scan_type: scanType
            })
        });
        return response.json();
    }
    
    async getDevices() {
        const response = await fetch(`${this.baseUrl}/devices/`, {
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const client = new MalsiftClient('http://localhost:8000/api/v1', 'your-token');
const scan = await client.createScan(['192.168.1.0/24']);
const devices = await client.getDevices();
```
