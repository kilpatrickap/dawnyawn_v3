# dawnyawn/agent/thought_engine.py (Final Version with Simplified Plan Update)
import re
import json
import logging
from pydantic import BaseModel
from pydantic_core import ValidationError
from config import get_llm_client, LLM_MODEL_NAME, LLM_REQUEST_TIMEOUT
from tools.tool_manager import ToolManager
from models.task_node import TaskNode
from typing import List, Dict


class ToolSelection(BaseModel):
    tool_name: str
    tool_input: str


# NEW: A Pydantic model for the simplified plan update response
class PlanUpdate(BaseModel):
    completed_task_ids: List[int]


def _clean_json_response(response_str: str) -> str:
    """Finds and extracts a JSON object from a string that might be wrapped in Markdown."""
    match = re.search(r'\{.*\}', response_str, re.DOTALL)
    if match:
        return match.group(0)
    return response_str


class ThoughtEngine:
    """AI Reasoning component. Decides the next action and assesses plan status."""

    def __init__(self, tool_manager: ToolManager):
        self.client = get_llm_client()
        self.tool_manager = tool_manager
        # This system prompt for choosing actions is now very solid.
        self.system_prompt_template = f"""
You are an expert penetration tester and command-line AI. Your SOLE function is to output a single, valid JSON object that represents the next best command to execute.

I. RESPONSE FORMATTING RULES (MANDATORY)
1.  **JSON ONLY:** Your entire response MUST be a single JSON object. Do not add explanations or any other text.
2.  **CORRECT SCHEMA:** The JSON object MUST have exactly two keys: `"tool_name"` and `"tool_input"`.
3.  **STRING INPUT:** The value for `"tool_input"` MUST be a single string.

II. STRATEGIC ANALYSIS & COMMAND RULES (HOW TO THINK)
1.  **FOCUS ON PENDING TASKS:** Look at the strategic plan and focus only on tasks with a 'PENDING' status.
2.  **DO NOT REPEAT SUCCESS:** NEVER repeat a command that has already been successfully executed and has completed a task.
3.  **SELF-TERMINATING COMMANDS:** Commands MUST be self-terminating (e.g., use `ping -c 4`, not `ping`).
4.  **DO NOT INSTALL ANY TOOL:**
5.  **Learn from Failures:** If a command fails, do not repeat it. Choose a different command.
6.  **Goal Completion:** Once all tasks in the plan are 'COMPLETED', you MUST use the `finish_mission` tool.

III. AVAILABLE TOOLS:
{self.tool_manager.get_tool_manifest()}
"""

    def _format_plan(self, plan: List[TaskNode]) -> str:
        if not plan: return "No plan provided."
        return "\n".join([f"  - Task {task.task_id} [{task.status}]: {task.description}" for task in plan])

    def choose_next_action(self, goal: str, plan: List[TaskNode], history: List[Dict]) -> ToolSelection:
        logging.info("🤔 Thinking about the next step...")

        user_prompt = (
            f"Based on the goal, plan, and history below, decide the single best command to execute next to progress on a PENDING task. Respond with a single, valid JSON object.\n\n"
            f"**Main Goal:** {goal}\n\n"
            f"**Strategic Plan:**\n{self._format_plan(plan)}\n\n"
            f"**Execution History (most recent last):\n{json.dumps(history, indent=2)}"
        )
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[{"role": "system", "content": self.system_prompt_template},
                          {"role": "user", "content": user_prompt}],
                timeout=LLM_REQUEST_TIMEOUT,
                response_format={"type": "json_object"},
                temperature=0.2
            )
            raw_response = response.choices[0].message.content
            selection = ToolSelection.model_validate_json(_clean_json_response(raw_response))
            logging.info("AI's Next Action: %s", selection.tool_input)
            return selection
        except (ValidationError, json.JSONDecodeError) as e:
            logging.error("Critical Error during thought process: %s", type(e).__name__)
            return ToolSelection(tool_name="finish_mission",
                                 tool_input="Mission failed: The AI produced an invalid JSON response.")

    # --- THE FIX: This method is now much simpler for the AI ---
    def get_completed_task_ids(self, goal: str, plan: List[TaskNode], history: List[Dict]) -> List[int]:
        """Asks the AI to identify which tasks are complete based on the latest action."""
        plan_update_prompt = (
            "You are a project manager AI. Review the strategic plan and the most recent entry in the execution history. "
            "Identify which task IDs from the plan are now fully completed by the last action's observation. "
            "Your response MUST be a single JSON object with one key: `\"completed_task_ids\"`, which is a list of integers. "
            "Example: `{\"completed_task_ids\": [1, 3]}`. If no tasks were completed, return an empty list.\n\n"
            f"**Strategic Plan:**\n{self._format_plan(plan)}\n\n"
            f"**Most Recent Action & Observation:**\n{json.dumps(history[-1], indent=2) if history else 'No actions yet.'}"
        )
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[{"role": "system", "content": "You are a JSON-only plan updating assistant."},
                          {"role": "user", "content": plan_update_prompt}],
                timeout=LLM_REQUEST_TIMEOUT,
                response_format={"type": "json_object"},
                temperature=0.0
            )
            raw_response = response.choices[0].message.content
            update = PlanUpdate.model_validate_json(_clean_json_response(raw_response))
            return update.completed_task_ids
        except (ValidationError, json.JSONDecodeError) as e:
            logging.error("AI failed to identify completed tasks with valid JSON: %s", e)
            return []  # Return an empty list on failure