# data-platform-mcp

A Model Context Protocol (MCP) server for interacting with data platform services.

## Overview

This project provides an MCP server that exposes data platform operations as tools, resources, and prompts that can be consumed by MCP-compatible clients (e.g. Claude Desktop, Claude Code).

## Requirements

- Python 3.10+
- An MCP-compatible client

## Installation

```bash
git clone https://github.com/lamvuvan/data-platform-mcp.git
cd data-platform-mcp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in the required credentials:

```bash
cp .env.example .env
```

## Usage

Run the MCP server locally:

```bash
python -m data_platform_mcp
```

To register the server with Claude Desktop, add an entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "data-platform": {
      "command": "python",
      "args": ["-m", "data_platform_mcp"]
    }
  }
}
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT
