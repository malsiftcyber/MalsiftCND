#!/bin/bash
# Quick script to rebuild Docker containers with updated frontend

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Rebuilding Docker containers with updated frontend...${NC}"

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

echo -e "${BLUE}Stopping containers...${NC}"
$DOCKER_SUDO $DOCKER_COMPOSE_CMD down

echo -e "${BLUE}Rebuilding images (this will rebuild the frontend)...${NC}"
$DOCKER_SUDO $DOCKER_COMPOSE_CMD build --no-cache

echo -e "${BLUE}Starting containers...${NC}"
$DOCKER_SUDO $DOCKER_COMPOSE_CMD up -d

echo -e "${GREEN}Done! Frontend has been rebuilt.${NC}"
echo -e "${BLUE}The web interface should now have the updated download functionality.${NC}"


