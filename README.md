# data-platform-mcp

A Model Context Protocol (MCP) server list for interacting with data platform services.

## Overview

This project provides an MCP server list that exposes data platform operations as tools, resources, and prompts that can be consumed by MCP-compatible clients (e.g. Claude Desktop, Claude Code).

## Requirements

- Python 3.10+
- An MCP-compatible client

## Configuration

Copy `.env.example` to `.env` and fill in the required credentials:

```bash
cp .env.example .env
```

## Development

```bash
pip install -r requirements.txt
pytest
```
