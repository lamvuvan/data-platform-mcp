import json
import unittest
from dotenv import load_dotenv

from mcp_server import list_databases, list_tables, get_schema, query_hive, initialize_connection, config

load_dotenv()

class TestMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load environment variables from .env file."""
        config.get_client_config()
        initialize_connection(
            host=config.host,
            port=config.port,
            auth=config.auth,
            username=config.username,
            password=config.password,
            database=config.database
        )

    def test_list_databases(self):
        """Test the list_databases function."""
        databases = list_databases()
        self.assertIsInstance(json.loads(databases)["databases"], list)
        self.assertGreater(len(databases), 0)

    def test_list_tables(self):
        """Test the list_tables function."""
        # databases = list_databases()
        # database = json.loads(databases)["databases"][0]
        database = "bi_retail_mart"
        tables = list_tables(database)
        self.assertIsInstance(json.loads(tables)["tables"], list)
        self.assertGreater(len(tables), 0)

    def test_get_schema(self):
        """Test the get_schema function."""
        # databases = list_databases()
        # database = json.loads(databases)["databases"][0]
        # tables = list_tables(database)
        # table = json.loads(tables)["tables"][0]
        database = "bi_retail_mart"
        table = "tbl_txn_for_retail_customer_report"
        schema = get_schema(database, table)
        self.assertIsInstance(json.loads(schema)["schema"], list)
        self.assertGreater(len(schema), 0)

    def test_query_hive(self):
        """Test the query_hive function."""
        database = "booking_timesheet_warehouse"
        table = "clocking_fact"
        query = f"SELECT * FROM {database}.{table} LIMIT 10"
        result = query_hive(query)
        self.assertIsInstance(json.loads(result)["results"], list)
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
