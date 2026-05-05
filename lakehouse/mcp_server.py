#!/usr/bin/env python3
"""
MCP Server for Apache Spark HiveServer2

This server connects to a Spark HiveServer2 database via Thrift JDBC and provides:
- Table schemas as resources
- Read-only SQL query tools
- Prompts for common data analysis tasks
"""

from mcp.server.fastmcp import FastMCP
from pyhive import hive
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
import re

from mcp_config import config

MCP_SERVER_NAME = "Lakehouse MCP Server"

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(MCP_SERVER_NAME)

load_dotenv()

class SparkHiveServer:
    def __init__(self, host: str, port: int, auth: str = 'LDAP', username: str = None, 
                 password: str = None, database: str = "default"):
        """Initialize connection to Spark-Hive via Thrift"""
        self.connection_params = {
            "host": host,
            "port": port,
            "auth": auth,
            "database": database
        }
        
        # Add authentication if provided
        if username:
            self.connection_params["username"] = username
        if password:
            self.connection_params["password"] = password
            
        # Test connection
        self._test_connection()
        
    def _test_connection(self):
        """Test the connection to Spark HiveServer2"""
        try:
            conn = hive.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            print("Successfully connected to Spark HiveServer2")
        except Exception as e:
            print(f"Failed to connect to Spark HiveServer2: {e}")
            raise
    
    def get_connection(self):
        """Get a connection to Spark HiveServer2"""
        return hive.connect(**self.connection_params)
    
    def get_databases(self) -> List[str]:
        """Get a list of all databases in the Spark HiveServer2 server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return databases
    
    def get_tables(self, database: str) -> List[str]:
        """Get a list of all tables in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SHOW TABLES IN {database}")
        tables = []
        for row in cursor.fetchall():
            tables.append(row[0] + "." + row[1])
        cursor.close()
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get the schema for a specific table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        schema = [{"name": row[0], "type": row[1], "comment": row[2] if len(row) > 2 else ""} 
                 for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return schema
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a read-only SQL query and return results"""
        # Validate that this is a read-only query
        if not self._is_read_only_query(query):
            raise ValueError("Only read-only queries are allowed")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            
            # Convert results to list of dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
        else:
            results = []
            
        cursor.close()
        conn.close()
        return results
    
    def _is_read_only_query(self, query: str) -> bool:
        """Check if a query is read-only"""
        # Convert to lowercase and remove comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        query = query.lower().strip()
        
        # Check if query starts with SELECT, SHOW, DESCRIBE, or EXPLAIN
        read_patterns = [
            r'^select\s+',
            r'^show\s+',
            r'^describe\s+',
            r'^desc\s+',
            r'^explain\s+'
        ]
        
        return any(re.match(pattern, query) for pattern in read_patterns)

# Create MCP server (Streamable HTTP transport, stateless + JSON responses)
mcp = FastMCP(
    MCP_SERVER_NAME,
    host=config.mcp_host,
    port=config.mcp_port,
    streamable_http_path=config.mcp_path,
    stateless_http=True,
    json_response=True,
)

@mcp.resource("databases://list")
def list_databases() -> str:
    """List all databases in the Spark HiveServer2 server"""
    if not spark_hive:
        return json.dumps({"error": "Not connected to Spark HiveServer2"})
    
    databases = spark_hive.get_databases()
    logger.info(f"Found {len(databases) if isinstance(databases, list) else 1} databases")
    return json.dumps({"databases": databases})

@mcp.tool("table_list")
def list_tables(database: str) -> str:
    """List all tables for a specific database"""
    if not spark_hive:
        return json.dumps({"error": "Not connected to Spark HiveServer2"})
    
    tables = spark_hive.get_tables(database)
    logger.info(f"Found {len(tables) if isinstance(tables, list) else 1} tables in {database}")
    return json.dumps({"tables": tables})

@mcp.tool("table_schema")
def get_schema(table: str) -> str:
    """Get schema for a specific table"""
    if not spark_hive:
        return json.dumps({"error": "Not connected to Spark HiveServer2"})
    
    try:
        schema = spark_hive.get_table_schema(table)
        return json.dumps({"table": table, "schema": schema})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def query(sql: str) -> str:
    """
    Execute a read-only SQL query on Spark HiveServer2
    
    Args:
        sql: SQL query to execute (must be read-only)
    
    Returns:
        Query results in JSON format
    """
    if not spark_hive:
        return json.dumps({"error": "Not connected to Spark HiveServer2"})
    
    try:
        # Log the query being executed
        logger.info(f"Executing query: {sql}")
        
        # Execute the query
        results = spark_hive.execute_query(sql)
        
        # Return results
        return json.dumps({"results": results}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def analyze_table(table: str, limit: int = 10) -> str:
    """
    Analyze a table and provide basic statistics
    
    Args:
        table: Name of the table to analyze
        limit: Maximum number of sample rows to return
    
    Returns:
        Table analysis in JSON format
    """
    if not spark_hive:
        return json.dumps({"error": "Not connected to Spark HiveServer2"})
    
    try:
        # Get schema
        schema = spark_hive.get_table_schema(table)
        
        # Get sample data
        sample_data = spark_hive.execute_query(f"SELECT * FROM {table} LIMIT {limit}")
        
        # Get row count
        count_result = spark_hive.execute_query(f"SELECT COUNT(*) as count FROM {table}")
        row_count = count_result[0]['count'] if count_result else 0
        
        # Get basic statistics for numeric columns
        stats = {}
        numeric_types = ['int', 'bigint', 'float', 'double', 'decimal']
        
        for column in schema:
            col_name = column['name']
            col_type = column['type']
            
            # Check if column type is numeric
            is_numeric = any(num_type in col_type.lower() for num_type in numeric_types)
            
            if is_numeric:
                # Get min, max, avg for numeric columns
                stats_query = f"""
                SELECT 
                    MIN({col_name}) as min_val,
                    MAX({col_name}) as max_val,
                    AVG({col_name}) as avg_val
                FROM {table}
                """
                col_stats = spark_hive.execute_query(stats_query)
                if col_stats:
                    stats[col_name] = col_stats[0]
        
        return json.dumps({
            "table": table,
            "row_count": row_count,
            "schema": schema,
            "statistics": stats,
            "sample_data": sample_data
        }, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.prompt()
def generate_query(table: str, columns: str = "*", filters: str = "", limit: int = 100) -> str:
    """
    Generate a SQL query for a specific table
    
    Args:
        table: Table name
        columns: Columns to select (comma-separated)
        filters: WHERE clause conditions
        limit: Maximum number of rows to return
    """
    where_clause = f" WHERE {filters}" if filters else ""
    return f"""
    Please execute this query to retrieve data from {table}:
    
    ```sql
    SELECT {columns}
    FROM {table}{where_clause}
    LIMIT {limit}
    ```
    """

@mcp.prompt()
def analyze_data_prompt(table: str) -> str:
    """
    Generate a prompt for analyzing a specific table
    
    Args:
        table: Table name to analyze
    """
    return f"""
    Please analyze the {table} table with the following steps:
    
    1. Examine the schema to understand the data structure
    2. Get basic statistics about the data
    3. Identify any patterns or anomalies
    4. Suggest potential insights or further analysis
    
    You can use the analyze_table tool to get started.
    """

def initialize_connection(host: str, port: int, auth: str = 'LDAP', username: str = None, 
                         password: str = None, database: str = "default"):
    """Initialize the connection to Spark HiveServer2"""
    global spark_hive
    spark_hive = SparkHiveServer(host, port, auth, username, password, database)


if __name__ == "__main__":
    config.get_client_config()
    
    try:
        initialize_connection(
            host=config.host,
            port=config.port,
            auth=config.auth,
            username=config.username,
            password=config.password,
            database=config.database
        )
        
        # Run the MCP server
        mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Error: {e}")
