# dawnyawn/services/mcp_client.py (NEW Simplified Version)
import requests
from typing import Tuple
from config import service_config

class McpClient:
    """Handles communication with the ephemeral execution server."""

    def execute_command(self, command: str) -> Tuple[str, str]:
        """
        Executes a command and returns the output filename and its content.
        Returns (None, error_message) on failure.
        """
        try:
            response = requests.post(
                f"{service_config.KALI_DRIVER_URL}/execute",
                json={"command": command},
                timeout=1800  # Long timeout for potentially long commands
            )
            response.raise_for_status()
            data = response.json()
            return data["filename"], data["file_content"]
        except requests.exceptions.RequestException as e:
            error_msg = f"Agent-side connection error: {e}"
            return None, error_msg