# dawnyawn/tools/tool_manager.py (Updated Version)
import os
import importlib
import logging
from tools.base_tool import BaseTool


class ToolManager:
    """Function Registry that dynamically loads and holds all available tools."""

    def __init__(self):
        """Initializes the ToolManager and triggers the tool discovery process."""
        self._tools: dict[str, BaseTool] = {}
        logging.info("Initializing ToolManager and discovering tools...")
        self._discover_and_register_tools()

    def _discover_and_register_tools(self):
        """Dynamically finds, imports, and registers tools from the 'tools' directory."""
        tools_dir = os.path.dirname(__file__)
        for filename in os.listdir(tools_dir):
            # Process only Python files, ignoring special files like __init__.py or base_tool.py
            if filename.endswith(".py") and not filename.startswith(("_", "base_tool")):
                module_name = f"tools.{filename[:-3]}"
                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)

                    # Scan the module for a class that inherits from BaseTool
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if isinstance(item, type) and issubclass(item, BaseTool) and item is not BaseTool:
                            tool_instance = item()
                            self._tools[tool_instance.name] = tool_instance
                            logging.info("Dynamically loaded tool: '%s'", tool_instance.name)
                            # Assuming one tool class per file for simplicity
                            break

                except ImportError as e:
                    logging.warning("Failed to import module %s. Error: %s", module_name, e)
                except Exception as e:
                    logging.error("An unexpected error occurred while loading tool from %s. Error: %s", module_name, e)

    def get_tool(self, tool_name: str) -> BaseTool:
        """Retrieves a registered tool by its name."""
        return self._tools.get(tool_name)

    def get_tool_manifest(self) -> str:
        """
        Returns a formatted string of all available tools for the LLM's system prompt.
        Includes the special 'finish_mission' command.
        """
        manifest = "Your response must select one of the following available tools:\n"

        # Add the special 'finish_mission' command to the manifest for the LLM
        manifest += (
            "- Tool Name: `finish_mission`\n"
            "  Description: Use this tool ONLY when you have fully accomplished the user's goal and have all the "
            "information needed. Provide a final, detailed summary of your findings as the input.\n"
        )

        # Add all dynamically loaded tools to the manifest
        if not self._tools:
            manifest += "\n- No other tools are currently available."
        else:
            for tool in self._tools.values():
                manifest += f"- Tool Name: `{tool.name}`\n  Description: {tool.description}\n"

        return manifest