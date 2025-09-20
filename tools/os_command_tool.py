# dawnyawn/tools/os_command_tool.py
from tools.base_tool import BaseTool
from services.mcp_client import McpClient

class OsCommandTool(BaseTool):
    """A tool for executing shell commands in a secure, isolated Kali environment."""
    name = "os_command"
    description = "Executes a single, non-interactive shell command (like nmap, whois, curl, dig) in a secure Kali Linux environment. Use this for all system-level commands and reconnaissance."

    def __init__(self):
        # The tool uses the MCP Client to communicate with the external server.
        self.mcp_client = McpClient()

    def execute(self, tool_input: str) -> str:
        print(f"  > Executing OS Command via Kali Driver: {tool_input}")
        return self.mcp_client.send_kali_command(tool_input)