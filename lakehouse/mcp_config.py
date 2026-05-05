from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class HiveServer2Config:
    """Configuration for HiveServer2 connection settings.

    This class handles all environment variable configuration with sensible defaults
    and type conversion. It provides typed methods for accessing each configuration value.

    Required environment variables:
        HIVESERVER2_HOST: The hostname of the HiveServer2 server
        HIVESERVER2_AUTH: The authentication method (default: NONE)
            Supported values: NONE, LDAP, KERBEROS, CUSTOM
            NONE: No authentication
            LDAP: LDAP authentication
            KERBEROS: Kerberos authentication
            CUSTOM: Custom authentication
        Note: The authentication method may affect the required environment variables.
        For example, if KERBEROS is used, additional variables such as
        KRB5_CONFIG, KRB5_KTNAME, and KRB5_REALM may be required.
        The following variables are required for all authentication methods:
        HIVESERVER2_USER: The username for authentication
        HIVESERVER2_PASSWORD: The password for authentication

    Optional environment variables (with defaults):
        HIVESERVER2_PORT: The port number (default: 10000)
        HIVESERVER2_CONNECT_TIMEOUT: Connection timeout in seconds (default: 30)
        HIVESERVER2_DATABASE: Default database to use (default: default)
    """

    def __init__(self):
        """Initialize the configuration from environment variables."""
        pass
        # self._validate_required_vars()

    @property
    def host(self) -> str:
        """Return the HiveServer2 host."""
        return os.environ.get("HIVESERVER2_HOST", "localhost")
    
    @property
    def auth(self) -> str:
        """Return the authentication method."""
        return os.environ.get("HIVESERVER2_AUTH", "NONE").upper()
    
    @property
    def username(self) -> str:
        """Return the HiveServer2 username."""
        return os.environ.get("HIVESERVER2_USERNAME", "")
    
    @property
    def password(self) -> str:
        """Return the HiveServer2 password."""
        return os.environ.get("HIVESERVER2_PASSWORD", "")
    
    @property
    def port(self) -> int:
        """Return the HiveServer2 port."""
        return int(os.environ.get("HIVESERVER2_PORT", 10000))
    
    @property
    def connect_timeout(self) -> int:
        """Return the connection timeout in seconds."""
        return int(os.environ.get("HIVESERVER2_CONNECT_TIMEOUT", 30))
    
    @property
    def database(self) -> Optional[str]:
        """Return the default database to use."""
        return os.environ.get("HIVESERVER2_DATABASE", "default")

    @property
    def mcp_host(self) -> str:
        """Return the host the MCP server binds to."""
        return os.environ.get("MCP_HOST", "0.0.0.0")

    @property
    def mcp_port(self) -> int:
        """Return the port the MCP server listens on."""
        return int(os.environ.get("MCP_PORT", 8000))

    @property
    def mcp_path(self) -> str:
        """Return the HTTP path exposing the MCP Streamable HTTP endpoint."""
        return os.environ.get("MCP_PATH", "/mcp")

    def get_client_config(self) -> dict:
        """Return the client configuration as a dictionary."""
        config = {
            "host": self.host,
            "port": self.port,
            "auth": self.auth,
            "username": self.username,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
            "database": self.database,
        }
        
        return config

    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set.

        Raises:
            ValueError: If any required environment variable is missing.
        """
        missing_vars = []
        for var in ["HIVESERVER2_HOST", "HIVESERVER2_USERNAME", "HIVESERVER2_PASSWORD"]:
            if var not in os.environ:
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


config = HiveServer2Config()
