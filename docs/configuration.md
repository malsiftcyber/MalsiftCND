# Configuration Guide

This guide covers all configuration options available in MalsiftCND.

## Environment Configuration

### Core Settings

**Application Configuration:**
```bash
# Application
APP_NAME=MalsiftCND
VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-secret-key-here-must-be-at-least-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-here-must-be-at-least-32-characters-long

# Database
DATABASE_URL=postgresql://malsift:malsift@localhost:5432/malsift

# Redis
REDIS_URL=redis://localhost:6379/0
```

**Security Settings:**
```bash
# Security
ALLOWED_HOSTS=["*"]
CORS_ORIGINS=["*"]

# SSL/TLS
SSL_KEYFILE=
SSL_CERTFILE=

# Authentication
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Scanning Configuration

**Scanner Settings:**
```bash
# Scanning
DEFAULT_SCAN_TIMEOUT=300
MAX_CONCURRENT_SCANS=10
SCAN_THROTTLE_RATE=100
```

**Nmap Configuration:**
```bash
# Nmap specific settings
NMAP_TIMEOUT=300
NMAP_MAX_RETRIES=3
NMAP_HOST_TIMEOUT=30s
NMAP_MAX_RTT_TIMEOUT=1s
```

**Masscan Configuration:**
```bash
# Masscan specific settings
MASSCAN_RATE=1000
MASSCAN_MAX_RATE=100000
MASSCAN_TIMEOUT=300
```

### AI/LLM Configuration

**OpenAI Integration:**
```bash
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=1000
```

**Anthropic Integration:**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_TEMPERATURE=0.1
ANTHROPIC_MAX_TOKENS=1000
```

**Groq Integration:**
```bash
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-8b-8192
GROQ_TEMPERATURE=0.1
GROQ_MAX_TOKENS=1000
```

### External Integrations

**RunZero Integration:**
```bash
RUNZERO_API_KEY=your-runzero-api-key
RUNZERO_BASE_URL=https://api.runzero.com/v1.0
RUNZERO_SYNC_INTERVAL=3600
RUNZERO_AUTO_SYNC=true
```

**Tanium Integration:**
```bash
TANIUM_API_KEY=your-tanium-api-key
TANIUM_BASE_URL=https://your-tanium-server.com
TANIUM_SYNC_INTERVAL=3600
TANIUM_AUTO_SYNC=true
```

**Armis Integration:**
```bash
ARMIS_API_KEY=your-armis-api-key
ARMIS_BASE_URL=https://your-armis-server.com
ARMIS_SYNC_INTERVAL=3600
ARMIS_AUTO_SYNC=true
```

**Active Directory Integration:**
```bash
AD_SERVER=ldap://dc.company.com
AD_DOMAIN=company.com
AD_USERNAME=malsift-service
AD_PASSWORD=service-password
AD_BASE_DN=DC=company,DC=com
AD_USER_SEARCH_BASE=CN=Users,DC=company,DC=com
```

**Azure AD Integration:**
```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
```

### Logging Configuration

**Log Settings:**
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=./logs/malsift.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
```

**Structured Logging:**
```bash
STRUCTURED_LOGGING=true
LOG_INCLUDE_TIMESTAMP=true
LOG_INCLUDE_LEVEL=true
LOG_INCLUDE_MODULE=true
```

### File Storage Configuration

**Storage Paths:**
```bash
DATA_DIR=./data
LOGS_DIR=./logs
CERTS_DIR=./certs
TEMP_DIR=./tmp
```

**File Permissions:**
```bash
DATA_DIR_PERMISSIONS=755
LOG_DIR_PERMISSIONS=755
CERT_DIR_PERMISSIONS=700
```

## Database Configuration

### PostgreSQL Settings

**Connection Settings:**
```python
# database.py
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False
}
```

**Performance Tuning:**
```sql
-- postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Redis Configuration

**Redis Settings:**
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

**Connection Pool:**
```python
# redis.py
REDIS_CONFIG = {
    "max_connections": 50,
    "retry_on_timeout": True,
    "socket_keepalive": True,
    "socket_keepalive_options": {}
}
```

## Web Server Configuration

### Nginx Configuration

**Basic Configuration:**
```nginx
server {
    listen 80;
    server_name malsift.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name malsift.company.com;
    
    ssl_certificate /etc/ssl/certs/malsift.crt;
    ssl_certificate_key /etc/ssl/private/malsift.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Security Headers:**
```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

### Apache Configuration

**Virtual Host:**
```apache
<VirtualHost *:443>
    ServerName malsift.company.com
    DocumentRoot /var/www/malsift
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/malsift.crt
    SSLCertificateKeyFile /etc/ssl/private/malsift.key
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
```

## Docker Configuration

### Docker Compose

**Production Configuration:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://malsift:malsift@db:5432/malsift
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./certs:/app/certs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=malsift
      - POSTGRES_USER=malsift
      - POSTGRES_PASSWORD=malsift
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Configuration

**Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: malsift-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: malsift-app
  template:
    metadata:
      labels:
        app: malsift-app
    spec:
      containers:
      - name: malsift-app
        image: malsift/app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: malsift-secrets
              key: database-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: malsift-service
spec:
  selector:
    app: malsift-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Monitoring Configuration

### Prometheus Configuration

**Prometheus Config:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'malsift'
    static_configs:
      - targets: ['malsift-app:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "MalsiftCND Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

**ELK Stack:**
```yaml
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "malsift" {
    json {
      source => "message"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "malsift-%{+YYYY.MM.dd}"
  }
}
```

## Security Configuration

### SSL/TLS Configuration

**LetEncrypt Setup:**
```bash
# certbot configuration
certbot certonly --standalone -d malsift.company.com
```

**Certificate Management:**
```bash
# Auto-renewal
0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration

**UFW Rules:**
```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow SSH (restrict to admin IPs)
ufw allow from 192.168.1.0/24 to any port 22

# Allow database connections (internal only)
ufw allow from 10.0.0.0/8 to any port 5432
ufw allow from 10.0.0.0/8 to any port 6379

# Deny all other traffic
ufw default deny incoming
ufw default allow outgoing
```

### Authentication Configuration

**LDAP Configuration:**
```python
# ldap_config.py
LDAP_CONFIG = {
    "server": "ldap://dc.company.com",
    "domain": "company.com",
    "base_dn": "DC=company,DC=com",
    "user_search_base": "CN=Users,DC=company,DC=com",
    "group_search_base": "CN=Groups,DC=company,DC=com"
}
```

**Azure AD Configuration:**
```python
# azure_config.py
AZURE_CONFIG = {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "authority": "https://login.microsoftonline.com/your-tenant-id",
    "scope": ["https://graph.microsoft.com/.default"]
}
```

## Performance Configuration

### Application Performance

**Worker Configuration:**
```python
# celery_config.py
CELERY_CONFIG = {
    "worker_concurrency": 4,
    "task_soft_time_limit": 300,
    "task_time_limit": 600,
    "worker_prefetch_multiplier": 1,
    "task_acks_late": True
}
```

**Caching Configuration:**
```python
# cache_config.py
CACHE_CONFIG = {
    "default_ttl": 3600,
    "max_connections": 50,
    "socket_keepalive": True,
    "socket_keepalive_options": {}
}
```

### Database Performance

**Connection Pooling:**
```python
# database.py
DATABASE_POOL_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False
}
```

**Query Optimization:**
```sql
-- Indexes for performance
CREATE INDEX CONCURRENTLY idx_devices_ip ON devices(ip);
CREATE INDEX CONCURRENTLY idx_devices_last_seen ON devices(last_seen);
CREATE INDEX CONCURRENTLY idx_scans_status ON scans(status);
CREATE INDEX CONCURRENTLY idx_scan_results_target ON scan_results(target_ip);
```

## Backup Configuration

### Database Backup

**Automated Backup:**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h localhost -U malsift malsift | gzip > "$BACKUP_DIR/malsift_$DATE.sql.gz"

# Cleanup old backups
find $BACKUP_DIR -name "malsift_*.sql.gz" -mtime +30 -delete
```

**Backup Schedule:**
```bash
# Crontab entry
0 2 * * * /opt/malsift/scripts/backup.sh
```

### Configuration Backup

**Configuration Backup:**
```bash
#!/bin/bash
# config_backup.sh
BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

tar -czf "$BACKUP_DIR/malsift_config_$DATE.tar.gz" \
  .env \
  docker-compose.yml \
  k8s/ \
  certs/ \
  scripts/
```

## Troubleshooting Configuration

### Debug Configuration

**Debug Mode:**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

**Verbose Logging:**
```python
# logging.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    }
}
```

### Health Check Configuration

**Health Check Endpoints:**
```python
# health.py
HEALTH_CHECK_CONFIG = {
    "database": True,
    "redis": True,
    "scanners": True,
    "integrations": True
}
```

**Monitoring Configuration:**
```yaml
# monitoring.yml
health_checks:
  - name: "database"
    url: "http://localhost:8000/health/database"
    interval: 30s
  - name: "redis"
    url: "http://localhost:8000/health/redis"
    interval: 30s
  - name: "scanners"
    url: "http://localhost:8000/health/scanners"
    interval: 60s
```
