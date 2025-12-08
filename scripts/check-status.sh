#!/bin/bash
# Quick script to check Docker container status and logs

# Detect docker compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
    DOCKER_SUDO=""
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
    DOCKER_SUDO=""
elif sudo docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
    DOCKER_SUDO="sudo"
elif sudo docker-compose --version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
    DOCKER_SUDO="sudo"
else
    echo "Error: Docker Compose not found"
    exit 1
fi

echo "=== Container Status ==="
$DOCKER_SUDO $DOCKER_COMPOSE_CMD ps

echo ""
echo "=== App Container Logs (last 30 lines) ==="
$DOCKER_SUDO $DOCKER_COMPOSE_CMD logs app --tail 30

echo ""
echo "=== Testing Health Endpoint ==="
curl -s http://localhost:8000/health || echo "Health endpoint not responding"

echo ""
echo "=== Testing Root Endpoint ==="
curl -s -I http://localhost:8000/ | head -5 || echo "Root endpoint not responding"


