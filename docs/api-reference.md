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
