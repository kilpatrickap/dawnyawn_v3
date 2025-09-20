# dawnyawn/agent/agent_scheduler.py (Simplified Text Version)
import re
from typing import List
from openai import APITimeoutError
from config import get_llm_client, LLM_MODEL_NAME, LLM_REQUEST_TIMEOUT
from models.task_node import TaskNode


class AgentScheduler:
    """LLM Orchestrator. Creates the high-level strategic plan for user review."""

    def __init__(self):
        self.client = get_llm_client()
        # --- THIS IS THE NEW, SIMPLIFIED TEXT PROMPT ---
        self.system_prompt = """
You are an EXPERT PENTESTING strategist. Your job is to convert a user's goal into a simple, NUMBERED list of high-level steps.

**Crucial Rules for Planning:**
1.  Your output MUST be a NUMBERED list, starting with "1.".
2.  Each item on the list should be a single, clear strategic step.
3.  Do not include specific commands, only the description of the step.
4.  Do not add any preamble, conversational text, or closing remarks.

**Example of a PERFECT response:**
User Goal: "Find the web server on example.com and see its homepage."
Your Response:
1. Scan example.com for open web ports to identify the web server.
2. If a web server is found, retrieve the content of its homepage.
"""

    def _parse_plan_from_text(self, text_plan: str) -> List[str]:
        """Parses a numbered list from the LLM's text response."""
        # Find all lines that start with a number followed by a period.
        steps = re.findall(r'^\s*\d+\.\s*(.*)', text_plan, re.MULTILINE)
        # Clean up any leading/trailing whitespace from the captured steps.
        return [step.strip() for step in steps]

    def create_plan(self, goal: str) -> List[TaskNode]:
        print(f"🗓️  Generating strategic plan for goal: '{goal}'")
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Goal: {goal}"}
                ],
                timeout=LLM_REQUEST_TIMEOUT
            )
            raw_text_plan = response.choices[0].message.content.strip()

            # --- PARSE THE TEXT RESPONSE ---
            task_descriptions = self._parse_plan_from_text(raw_text_plan)

            if not task_descriptions:
                print("\n❌ Critical Error: The AI model failed to generate a valid, numbered plan.")
                print(f"   Model's raw response: \"{raw_text_plan}\"")
                return []

            # Convert the list of strings into a list of TaskNode objects
            return [TaskNode(task_id=i + 1, description=desc) for i, desc in enumerate(task_descriptions)]

        except APITimeoutError:
            print("\n❌ Critical Error: The AI model timed out while creating the plan.")
            return []