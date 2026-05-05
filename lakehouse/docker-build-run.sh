#!/bin/bash
set -euo pipefail

# Build and (re)start the MCP server via Docker Compose.
# The image name (lakehouse-mcp-server:latest) is defined in docker-compose.yml.
echo "Building and starting lakehouse MCP server..."
docker compose up -d --build
echo "MCP server is up at http://localhost:${MCP_PORT:-8000}${MCP_PATH:-/mcp}"
