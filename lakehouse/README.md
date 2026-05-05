# Spark-HiveServer2 MCP Server

This is a Model Context Protocol (MCP) server that connects to Apache Spark HiveServer2 via Thrift JDBC. It provides a standardized way for LLMs to interact with your Spark HiveServer2 database.

## Features

- **Table Schema Tools**: Access table schemas
- **Read-Only SQL Tools**: Execute read-only SQL queries against your Spark HiveServer2 database
- **Data Analysis Tools**: Analyze tables and get basic statistics
- **Prompt Templates**: Common data analysis prompts for LLMs

### Tools

- list_databases: Get all databases (datasets) on Spark HiveServer2
- list_tables: Get all tables in a database (dataset)
- get_schema: Get schema for a table in a database
- query: Execute SQL query on Spark HiveServer2 using Thrift JDBC
- analyze_table: Analyze a table and provide basic statistics

## Installation

### Prerequisites

- Python 3.10+
- Access to a Spark HiveServer2 Thrift server

### Setup Options

#### Option 1: Docker (recommended)

1. Make sure Docker and Docker Compose are installed.

2. Copy and fill in the environment file:

```bash
cp .env.template .env
# edit .env with your HiveServer2 credentials
```

3. Build and start the container:

```bash
docker compose up -d --build
```

The server will be reachable at `http://localhost:8000/mcp`. Check logs with `docker compose logs -f mcp-server`.

To stop:

```bash
docker compose down
```

#### Option 2: Direct Installation

1. Install the required Python packages:

```bash
python3 -m pip install -r requirements.txt
```

2. Copy `.env.template` to `.env`, fill in credentials, then run:

```bash
python3 mcp_server.py
```

## Configuration

### Environment variables

Copy `.env.template` to `.env` and fill in your values. HiveServer2 vars control the backend connection; `MCP_*` vars control the MCP HTTP transport.

| Variable | Default | Description |
|----------|---------|-------------|
| `HIVESERVER2_HOST` | — | HiveServer2 Thrift host |
| `HIVESERVER2_PORT` | `10000` | HiveServer2 Thrift port |
| `HIVESERVER2_AUTH` | `NONE` | `NONE`, `LDAP`, `KERBEROS`, or `CUSTOM` |
| `HIVESERVER2_USERNAME` | — | Auth username |
| `HIVESERVER2_PASSWORD` | — | Auth password |
| `HIVESERVER2_DATABASE` | `default` | Default database |
| `MCP_HOST` | `0.0.0.0` | Interface the MCP server binds to |
| `MCP_PORT` | `8000` | Port the MCP server listens on |
| `MCP_PATH` | `/mcp` | HTTP path for the Streamable HTTP endpoint |

### Client configuration (Claude Desktop, Cline, etc.)

The server uses the MCP **Streamable HTTP** transport (the successor to the older SSE transport) and runs inside a Docker container that publishes a single HTTP endpoint at `http://<host>:<MCP_PORT><MCP_PATH>` (default `http://localhost:8000/mcp`).

Start the server first with `docker compose up -d --build`, then point your MCP client at the endpoint. Claude Desktop does not yet speak Streamable HTTP to local servers natively, so use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge:

```json
{
  "mcpServers": {
    "lakehouse": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8000/mcp"
      ],
      "autoApprove": ["query"]
    }
  }
}
```

Claude Desktop config path:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Cline config path on macOS: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`.

## Usage

### Starting the server

With Docker (recommended):

```bash
docker compose up -d --build
docker compose logs -f mcp-server   # tail logs
```

Or directly with Python:

```bash
python3 mcp_server.py
```

Either way you should see a Uvicorn banner indicating the server is listening on `http://0.0.0.0:8000`.

### Smoke-test the endpoint

```bash
curl -sS -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

### Inspect tools interactively

```bash
npx -y @modelcontextprotocol/inspector http://localhost:8000/mcp
```

## MCP Resources

The server exposes the following resources:
- `databases://list` - Lists all databases


## MCP Tools

The server provides the following tools:
- `tables://{database}` - Lists all tables in a database
- `schema://{database}.{table}` - Gets the schema for a specific table
- `query_hive(sql: str)` - Executes a read-only SQL query and returns the results
- `analyze_table(table: str, limit: int = 10)` - Analyzes a table and provides basic statistics

## MCP Prompts

The server includes the following prompt templates:

- `generate_query(table: str, columns: str = "*", filters: str = "", limit: int = 100)` - Generates a SQL query for a specific table
- `analyze_data_prompt(table: str)` - Generates a prompt for analyzing a specific table

## Examples

### Listing Tables

```
Use the tables://list resource to list all tables in the database.
```

### Getting a Table Schema

```
Use the schema://employees resource to get the schema for the employees table.
```

### Executing a Query

```
Use the query tool to execute the following SQL query:
SELECT * FROM employees WHERE department = 'Engineering' LIMIT 10
```

### Analyzing a Table

```
Use the analyze_table tool to analyze the employees table.
```

## Security Considerations

- The server only allows read-only queries to protect your data
- Authentication credentials can be provided for secure connections
- All SQL queries are validated before execution

## Limitations

- Only read-only queries are supported (SELECT, SHOW, DESCRIBE, EXPLAIN)
- Large result sets may impact performance
- Complex queries may timeout depending on your Spark-Hive configuration

## Troubleshooting

If you encounter connection issues:

1. Verify that your Spark HiveServer2 server is running and accessible
2. Check that the host and port are correct
3. Ensure that your authentication credentials are valid
4. Confirm that the specified database exists
