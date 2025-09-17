# Admin Manual

This manual provides comprehensive guidance for administrators managing MalsiftCND in enterprise environments.

## System Administration

### User Management

#### Creating Users

**Via Web Interface:**
1. Navigate to Admin → Users
2. Click "Create User"
3. Fill in user details:
   - Username (unique)
   - Email address
   - Password (strong password required)
   - Admin privileges (if applicable)

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@company.com",
    "password": "SecurePassword123!",
    "is_admin": false
  }'
```

#### Managing User Permissions

**Role-Based Access Control:**
- **Admin**: Full system access, user management, system configuration
- **Operator**: Scan management, device viewing, report generation
- **Viewer**: Read-only access to scans and devices

**Permission Matrix:**
| Action | Admin | Operator | Viewer |
|--------|-------|----------|--------|
| Create Scans | ✓ | ✓ | ✗ |
| View Scans | ✓ | ✓ | ✓ |
| Manage Users | ✓ | ✗ | ✗ |
| System Config | ✓ | ✗ | ✗ |
| View Devices | ✓ | ✓ | ✓ |
| Export Data | ✓ | ✓ | ✗ |

#### Multi-Factor Authentication

**Enabling MFA:**
1. Navigate to Profile → Security
2. Click "Enable Two-Factor Authentication"
3. Scan QR code with authenticator app
4. Enter verification code
5. Save backup codes securely

**MFA Recovery:**
- Use backup codes for account recovery
- Admin can disable MFA for locked users
- Contact support for account recovery

### System Configuration

#### Scanner Configuration

**Nmap Scanner Settings:**
```yaml
nmap:
  enabled: true
  timeout: 300
  rate_limit: null
  custom_args: "-T4 --max-retries 3"
  max_hosts_per_scan: 1000
```

**Masscan Scanner Settings:**
```yaml
masscan:
  enabled: true
  timeout: 300
  rate_limit: 1000
  custom_args: "--max-rate 1000"
  max_hosts_per_scan: 10000
```

**Scanner Performance Tuning:**
- Adjust `rate_limit` based on network capacity
- Increase `max_concurrent_scans` for faster processing
- Use `custom_args` for specific scan requirements

#### AI Analysis Configuration

**LLM Provider Settings:**
```yaml
ai_analysis:
  enabled: true
  providers:
    openai:
      enabled: true
      model: "gpt-4"
      temperature: 0.1
      max_tokens: 1000
    anthropic:
      enabled: true
      model: "claude-3-sonnet-20240229"
      temperature: 0.1
      max_tokens: 1000
    groq:
      enabled: true
      model: "llama3-8b-8192"
      temperature: 0.1
      max_tokens: 1000
```

**AI Analysis Best Practices:**
- Use multiple providers for redundancy
- Monitor API usage and costs
- Adjust confidence thresholds as needed
- Review AI analysis accuracy regularly

#### Integration Management

**RunZero Integration:**
```yaml
runzero:
  enabled: true
  api_key: "your-api-key"
  base_url: "https://api.runzero.com/v1.0"
  sync_interval: 3600
  auto_sync: true
```

**Active Directory Integration:**
```yaml
active_directory:
  enabled: true
  server: "ldap://dc.company.com"
  domain: "company.com"
  username: "malsift-service"
  password: "service-password"
  base_dn: "DC=company,DC=com"
  user_search_base: "CN=Users,DC=company,DC=com"
```

**Azure AD Integration:**
```yaml
azure_ad:
  enabled: true
  tenant_id: "your-tenant-id"
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  authority: "https://login.microsoftonline.com/your-tenant-id"
```

### Security Management

#### SSL/TLS Configuration

**LetEncrypt Setup:**
```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d malsift.company.com

# Update configuration
SSL_KEYFILE=/etc/letsencrypt/live/malsift.company.com/privkey.pem
SSL_CERTFILE=/etc/letsencrypt/live/malsift.company.com/fullchain.pem
```

**Enterprise Certificate Setup:**
```bash
# Copy certificates
cp company-cert.pem certs/
cp company-key.pem certs/

# Update configuration
SSL_KEYFILE=./certs/company-key.pem
SSL_CERTFILE=./certs/company-cert.pem
```

#### Security Policies

**Password Policy:**
- Minimum 12 characters
- Must include uppercase, lowercase, numbers, symbols
- Cannot reuse last 5 passwords
- Expires every 90 days

**Session Management:**
- Session timeout: 30 minutes
- Concurrent sessions: 3 per user
- IP restrictions: Configurable per user

**API Security:**
- Rate limiting: 100 requests/minute
- Token expiration: 30 minutes
- Refresh tokens: 7 days
- IP whitelisting: Optional

### Monitoring and Maintenance

#### System Monitoring

**Key Metrics to Monitor:**
- CPU usage (should be < 80%)
- Memory usage (should be < 85%)
- Disk space (should be < 90%)
- Database connections (should be < 80% of max)
- Scan queue length (should be < 100)

**Alert Thresholds:**
```yaml
alerts:
  cpu_usage:
    warning: 80
    critical: 90
  memory_usage:
    warning: 85
    critical: 95
  disk_space:
    warning: 85
    critical: 95
  scan_queue:
    warning: 50
    critical: 100
```

#### Log Management

**Log Rotation:**
```bash
# /etc/logrotate.d/malsift
/var/log/malsift/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 malsift malsift
}
```

**Log Analysis:**
- Monitor authentication failures
- Track scan performance
- Identify security events
- Monitor API usage

#### Database Maintenance

**Regular Maintenance Tasks:**
```sql
-- Analyze tables for query optimization
ANALYZE;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Reindex for performance
REINDEX DATABASE malsift;
```

**Backup Strategy:**
- Daily full backups
- Hourly incremental backups
- Test restore procedures monthly
- Store backups offsite

### Troubleshooting

#### Common Issues

**Scan Failures:**
1. Check scanner availability (`nmap --version`, `masscan --version`)
2. Verify network connectivity to targets
3. Check firewall rules
4. Review scan logs for errors

**Database Connection Issues:**
1. Verify PostgreSQL is running
2. Check connection string in configuration
3. Test database connectivity
4. Review database logs

**Authentication Problems:**
1. Check user account status
2. Verify password policy compliance
3. Test LDAP/AD connectivity
4. Review authentication logs

**Performance Issues:**
1. Monitor system resources
2. Check database performance
3. Review scan queue length
4. Analyze slow queries

#### Diagnostic Commands

**System Health Check:**
```bash
# Check application status
curl http://localhost:8000/health

# Check database connectivity
psql -h localhost -U malsift -d malsift -c "SELECT 1;"

# Check Redis connectivity
redis-cli ping

# Check scanner availability
nmap --version
masscan --version
```

**Log Analysis:**
```bash
# View application logs
tail -f /var/log/malsift/app.log

# Search for errors
grep -i error /var/log/malsift/*.log

# Monitor scan activity
grep "scan" /var/log/malsift/scan.log
```

### Backup and Recovery

#### Backup Procedures

**Database Backup:**
```bash
#!/bin/bash
# daily_backup.sh
BACKUP_DIR="/backups/malsift"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U malsift malsift | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env certs/ k8s/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

**Configuration Backup:**
```bash
# Backup all configuration files
tar -czf malsift_config_$(date +%Y%m%d).tar.gz \
  .env \
  docker-compose.yml \
  k8s/ \
  certs/ \
  scripts/
```

#### Recovery Procedures

**Database Recovery:**
```bash
# Stop application
docker-compose down

# Restore database
gunzip -c db_20240101_120000.sql.gz | psql -h localhost -U malsift malsift

# Start application
docker-compose up -d
```

**Full System Recovery:**
1. Restore from backup
2. Update configuration
3. Restart services
4. Verify functionality
5. Test critical operations

### Performance Optimization

#### Database Optimization

**Query Optimization:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_devices_ip ON devices(ip);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scan_results_target ON scan_results(target_ip);
```

**Connection Pooling:**
```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

#### Application Optimization

**Worker Scaling:**
```yaml
# docker-compose.yml
services:
  worker:
    deploy:
      replicas: 4
    environment:
      - CELERY_WORKER_CONCURRENCY=4
```

**Caching Strategy:**
```python
# Use Redis for caching
CACHE_TTL = 3600  # 1 hour
CACHE_PREFIX = "malsift:"
```

### Compliance and Auditing

#### Audit Requirements

**SOX Compliance:**
- User access reviews quarterly
- Audit trail maintenance
- Data integrity verification
- Change management procedures

**GDPR Compliance:**
- Data encryption at rest and in transit
- Data retention policies
- Right to be forgotten procedures
- Privacy impact assessments

**PCI DSS Compliance:**
- Network segmentation
- Access controls
- Regular security testing
- Incident response procedures

#### Audit Procedures

**User Access Review:**
1. Generate user access report
2. Review with department managers
3. Remove unnecessary access
4. Document changes

**Security Audit:**
1. Review authentication logs
2. Check for failed login attempts
3. Verify MFA compliance
4. Review API access patterns

**Data Audit:**
1. Verify data integrity
2. Check backup completeness
3. Review data retention compliance
4. Validate encryption status
