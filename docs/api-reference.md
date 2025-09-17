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

### EDR Integration

#### POST /edr/integrations
Create a new EDR integration.

**Request Body:**
```json
{
  "name": "CrowdStrike Production",
  "provider": "crowdstrike",
  "api_base_url": "https://api.crowdstrike.com",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "auth_type": "oauth",
  "sync_enabled": true,
  "sync_interval_minutes": 60,
  "sync_endpoints": true,
  "sync_alerts": false,
  "sync_vulnerabilities": false,
  "sync_network_connections": false,
  "company_id": "uuid",
  "site_id": "uuid",
  "description": "Production CrowdStrike integration"
}
```

#### GET /edr/integrations
List all EDR integrations.

**Query Parameters:**
- `active_only`: Show only active integrations (default: true)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "CrowdStrike Production",
    "provider": "crowdstrike",
    "api_base_url": "https://api.crowdstrike.com",
    "auth_type": "oauth",
    "is_active": true,
    "sync_enabled": true,
    "sync_interval_minutes": 60,
    "sync_endpoints": true,
    "sync_alerts": false,
    "last_sync": "2024-01-15T10:30:00Z",
    "next_sync": "2024-01-15T11:30:00Z",
    "company_id": "uuid",
    "site_id": "uuid",
    "description": "Production CrowdStrike integration",
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /edr/integrations/{integration_id}
Get EDR integration by ID.

#### PUT /edr/integrations/{integration_id}
Update EDR integration.

#### DELETE /edr/integrations/{integration_id}
Delete EDR integration (soft delete).

#### POST /edr/integrations/{integration_id}/test
Test EDR integration connectivity.

**Response:**
```json
{
  "status": "success",
  "authentication": "success",
  "endpoints_accessible": true,
  "endpoint_count": 150
}
```

#### POST /edr/integrations/{integration_id}/sync
Manually sync EDR integration.

**Response:**
```json
{
  "status": "success",
  "records_processed": 150,
  "records_created": 5,
  "records_updated": 145,
  "records_failed": 0,
  "duration_seconds": 45
}
```

#### GET /edr/integrations/{integration_id}/endpoints
Get endpoints from EDR integration.

**Query Parameters:**
- `limit`: Number of endpoints to return (default: 100)
- `offset`: Number of endpoints to skip (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "edr_endpoint_id": "edr_12345",
    "edr_hostname": "workstation-01",
    "edr_ip_addresses": ["192.168.1.100"],
    "hostname": "workstation-01",
    "operating_system": "Windows 10",
    "os_version": "10.0.19042",
    "architecture": "x64",
    "processor": "Intel Core i7",
    "memory_gb": 16.0,
    "mac_addresses": ["00:11:22:33:44:55"],
    "agent_version": "6.45.0",
    "agent_status": "online",
    "last_seen_by_agent": "2024-01-15T10:30:00Z",
    "risk_score": 7.5,
    "threat_level": "medium",
    "compliance_status": "compliant",
    "edr_tags": ["production", "workstation"],
    "edr_groups": ["Workstations"],
    "device_id": "uuid",
    "company_id": "uuid",
    "site_id": "uuid",
    "first_seen": "2024-01-15T00:00:00Z",
    "last_seen": "2024-01-15T10:30:00Z",
    "last_updated": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /edr/integrations/{integration_id}/alerts
Get alerts from EDR integration.

**Query Parameters:**
- `limit`: Number of alerts to return (default: 100)
- `offset`: Number of alerts to skip (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "edr_alert_id": "alert_12345",
    "edr_incident_id": "incident_67890",
    "alert_type": "Malware Detection",
    "severity": "high",
    "status": "open",
    "title": "Malware Detected on Workstation",
    "description": "Suspicious file detected and quarantined",
    "threat_name": "Trojan.Generic",
    "threat_type": "malware",
    "threat_category": "trojan",
    "ioc_count": 3,
    "detected_at": "2024-01-15T10:30:00Z",
    "resolved_at": null,
    "endpoint_id": "uuid",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /edr/integrations/{integration_id}/sync-logs
Get sync logs for EDR integration.

**Query Parameters:**
- `limit`: Number of logs to return (default: 50)
- `offset`: Number of logs to skip (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "sync_type": "endpoints",
    "status": "success",
    "started_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:31:00Z",
    "duration_seconds": 60,
    "records_processed": 150,
    "records_created": 5,
    "records_updated": 145,
    "records_failed": 0,
    "error_message": null,
    "error_details": null
  }
]
```

#### GET /edr/providers
Get available EDR providers and their configuration requirements.

**Response:**
```json
{
  "providers": [
    {
      "name": "CrowdStrike Falcon",
      "value": "crowdstrike",
      "description": "CrowdStrike Falcon EDR platform",
      "auth_types": ["oauth"],
      "required_fields": ["api_base_url", "client_id", "client_secret"],
      "optional_fields": ["tenant_id"],
      "api_documentation": "https://falcon.crowdstrike.com/documentation"
    },
    {
      "name": "Microsoft Defender for Endpoint",
      "value": "microsoft_defender",
      "description": "Microsoft Defender for Endpoint EDR platform",
      "auth_types": ["oauth"],
      "required_fields": ["tenant_id", "client_id", "client_secret"],
      "optional_fields": [],
      "api_documentation": "https://docs.microsoft.com/en-us/microsoft-365/security/defender-endpoint/"
    },
    {
      "name": "SentinelOne",
      "value": "sentinelone",
      "description": "SentinelOne EDR platform",
      "auth_types": ["api_key"],
      "required_fields": ["api_base_url", "client_id", "client_secret"],
      "optional_fields": [],
      "api_documentation": "https://usea1-partners.sentinelone.net/api-doc/"
    },
    {
      "name": "TrendMicro Vision One",
      "value": "trendmicro",
      "description": "TrendMicro Vision One EDR platform",
      "auth_types": ["api_key"],
      "required_fields": ["api_base_url", "api_key"],
      "optional_fields": [],
      "api_documentation": "https://automation.trendmicro.com/vision-one/api"
    }
  ]
}
```

### Accuracy Ranking

#### GET /accuracy/data-sources
List all data sources with their accuracy metrics.

**Query Parameters:**
- `active_only`: Show only active sources (default: true)
- `ranked_only`: Show only ranked sources (default: false)

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "CrowdStrike Falcon",
    "source_type": "edr_platform",
    "provider": "crowdstrike",
    "version": "6.45.0",
    "description": "Endpoint detection and response platform",
    "is_active": true,
    "is_ai_evaluated": true,
    "manual_rank_override": null,
    "current_accuracy_score": 0.95,
    "confidence_level": 0.92,
    "current_rank": 1,
    "previous_rank": 2,
    "rank_change": 1,
    "total_evaluations": 1250,
    "successful_evaluations": 1187,
    "failed_evaluations": 63,
    "average_response_time_ms": 450.0,
    "success_rate": 0.95,
    "data_completeness_score": 0.88,
    "last_evaluation": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### POST /accuracy/data-sources
Create a new data source.

**Request Body:**
```json
{
  "name": "Custom Scanner",
  "source_type": "network_scanner",
  "provider": "custom",
  "version": "1.0.0",
  "description": "Custom network scanner",
  "is_active": true,
  "is_ai_evaluated": true,
  "manual_rank_override": null
}
```

#### GET /accuracy/data-sources/{source_id}
Get data source by ID.

#### PUT /accuracy/data-sources/{source_id}
Update data source.

#### POST /accuracy/data-sources/{source_id}/evaluate
Evaluate data source accuracy.

**Request Body:**
```json
{
  "evaluation_type": "device_identification",
  "sample_size": 100
}
```

**Response:**
```json
{
  "data_source_id": "uuid",
  "evaluation_type": "device_identification",
  "total_evaluations": 100,
  "average_accuracy": 0.87,
  "average_confidence": 0.82,
  "average_response_time_ms": 1200.0,
  "data_completeness": 0.75,
  "success_rate": 0.95
}
```

#### POST /accuracy/rankings/calculate
Calculate and update data source rankings.

**Response:**
```json
{
  "ranking_calculated": true,
  "total_sources": 8,
  "ranking_period": "2024-01-08T00:00:00Z to 2024-01-15T00:00:00Z",
  "algorithm_version": "1.0",
  "rankings": [
    {
      "rank": 1,
      "source_name": "CrowdStrike Falcon",
      "source_type": "edr_platform",
      "composite_score": 0.92,
      "accuracy_score": 0.95,
      "confidence_level": 0.92,
      "rank_change": 1
    }
  ]
}
```

#### GET /accuracy/rankings
Get historical rankings.

**Query Parameters:**
- `limit`: Number of rankings to return (default: 50)
- `offset`: Number of rankings to skip (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "data_source_id": "uuid",
    "data_source_name": "CrowdStrike Falcon",
    "rank": 1,
    "accuracy_score": 0.95,
    "confidence_level": 0.92,
    "total_evaluations": 1250,
    "successful_evaluations": 1187,
    "failed_evaluations": 63,
    "average_response_time_ms": 450.0,
    "success_rate": 0.95,
    "data_completeness_score": 0.88,
    "ranking_period_start": "2024-01-08T00:00:00Z",
    "ranking_period_end": "2024-01-15T00:00:00Z",
    "ranking_algorithm_version": "1.0",
    "created_at": "2024-01-15T00:00:00Z"
  }
]
```

#### GET /accuracy/dashboard
Get accuracy ranking dashboard data.

**Query Parameters:**
- `dashboard_id`: Specific dashboard ID (optional)

**Response:**
```json
{
  "summary": {
    "total_sources": 8,
    "average_accuracy": 0.87,
    "average_confidence": 0.82,
    "recent_evaluations": 150,
    "active_alerts": 3,
    "last_ranking_update": "2024-01-15T10:30:00Z"
  },
  "rankings": [
    {
      "rank": 1,
      "name": "CrowdStrike Falcon",
      "source_type": "edr_platform",
      "provider": "crowdstrike",
      "accuracy_score": 0.95,
      "confidence_level": 0.92,
      "success_rate": 0.95,
      "data_completeness": 0.88,
      "average_response_time_ms": 450.0,
      "total_evaluations": 1250,
      "rank_change": 1,
      "last_evaluation": "2024-01-15T10:30:00Z",
      "is_ai_evaluated": true,
      "manual_rank_override": null
    }
  ],
  "accuracy_trends": {
    "period": "30_days",
    "trends": [
      {
        "date": "2024-01-15",
        "average_accuracy": 0.87,
        "source_count": 8
      }
    ]
  },
  "performance_metrics": {
    "response_time": {
      "average_ms": 850.0,
      "min_ms": 200.0,
      "max_ms": 3000.0
    },
    "success_rate": {
      "average": 0.92,
      "min": 0.75,
      "max": 0.98
    },
    "data_completeness": {
      "average": 0.82,
      "min": 0.60,
      "max": 0.95
    }
  }
}
```

#### POST /accuracy/dashboard
Create a new accuracy dashboard.

**Request Body:**
```json
{
  "name": "Executive Dashboard",
  "description": "High-level accuracy metrics for executives",
  "refresh_interval_minutes": 30,
  "source_type_filter": ["edr_platform", "network_scanner"],
  "time_range_days": 30,
  "min_accuracy_threshold": 0.8
}
```

#### GET /accuracy/alerts
Get accuracy alerts.

**Query Parameters:**
- `active_only`: Show only active alerts (default: true)
- `severity`: Filter by severity level (optional)
- `limit`: Number of alerts to return (default: 50)
- `offset`: Number of alerts to skip (default: 0)

**Response:**
```json
[
  {
    "id": "uuid",
    "data_source_id": "uuid",
    "data_source_name": "Nmap Scanner",
    "alert_type": "accuracy_drop",
    "severity": "high",
    "title": "Significant Accuracy Drop: Nmap Scanner",
    "description": "Accuracy dropped from 85% to 72%",
    "alert_data": {
      "previous_accuracy": 0.85,
      "current_accuracy": 0.72,
      "drop_percentage": 15.3
    },
    "threshold_value": 10.0,
    "actual_value": 15.3,
    "change_percentage": 15.3,
    "is_active": true,
    "is_acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "triggered_at": "2024-01-15T10:30:00Z",
    "resolved_at": null,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### POST /accuracy/alerts/{alert_id}/acknowledge
Acknowledge an accuracy alert.

**Response:**
```json
{
  "message": "Alert 'uuid' acknowledged successfully"
}
```

#### GET /accuracy/metrics
Get accuracy metrics over time.

**Query Parameters:**
- `period`: Metric period (hourly, daily, weekly, monthly)
- `days`: Number of days to include (1-365)

**Response:**
```json
{
  "period": "daily",
  "days": 30,
  "start_date": "2023-12-16T00:00:00Z",
  "end_date": "2024-01-15T00:00:00Z",
  "metrics_by_source": {
    "uuid": {
      "source_name": "CrowdStrike Falcon",
      "source_type": "edr_platform",
      "metrics": [
        {
          "date": "2024-01-15",
          "accuracy_score": 0.95,
          "confidence_level": 0.92,
          "total_evaluations": 50,
          "success_rate": 0.96,
          "data_completeness": 0.88,
          "rank": 1,
          "rank_change": 0
        }
      ]
    }
  }
}
```

#### POST /accuracy/initialize
Initialize the accuracy ranking system with default data sources.

**Response:**
```json
{
  "message": "Accuracy ranking system initialized successfully"
}
```

#### GET /accuracy/source-types
Get available data source types.

**Response:**
```json
{
  "source_types": [
    {
      "value": "network_scanner",
      "name": "Network Scanner",
      "description": "Network discovery and port scanning tools"
    },
    {
      "value": "edr_platform",
      "name": "EDR Platform",
      "description": "Endpoint detection and response platforms"
    },
    {
      "value": "asm_tool",
      "name": "ASM Tool",
      "description": "Attack surface management tools"
    },
    {
      "value": "directory_service",
      "name": "Directory Service",
      "description": "Active Directory and Azure AD services"
    },
    {
      "value": "ai_analysis",
      "name": "AI Analysis",
      "description": "AI-powered analysis and identification"
    },
    {
      "value": "user_correction",
      "name": "User Correction",
      "description": "Manual user corrections and verifications"
    }
  ]
}
```

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
