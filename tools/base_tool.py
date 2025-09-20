# dawnyawn/tools/base_tool.py
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Abstract base class for all tools available to the agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool, used by the Thought Engine for selection."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A clear description of what the tool does, for the LLM to understand its purpose."""
        pass

    @abstractmethod
    def execute(self, tool_input: str) -> str:
        """Executes the tool with the given input and returns the raw string result."""
        pass