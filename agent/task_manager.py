# dawnyawn/agent/task_manager.py (Final Version with Simplified Plan Update Logic)
import os
import json
import logging
from openai import APITimeoutError
from models.task_node import TaskNode, TaskStatus
from reporting.report_generator import create_report

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(PROJECT_ROOT, "Projects")
SESSION_FILE = os.path.join(PROJECTS_DIR, "mission_session.json")


class TaskManager:
    """Orchestrates the agent's lifecycle with dynamic plan status updates."""

    def __init__(self, goal: str):
        from agent.agent_scheduler import AgentScheduler
        from agent.thought_engine import ThoughtEngine
        from tools.tool_manager import ToolManager
        from services.mcp_client import McpClient

        self.goal = goal
        self.plan: list[TaskNode] = []
        self.mission_history = []
        self.scheduler = AgentScheduler()
        self.thought_engine = ThoughtEngine(ToolManager())
        self.mcp_client = McpClient()
        os.makedirs(PROJECTS_DIR, exist_ok=True)

    def initialize_mission(self):
        """Asks user whether to resume an old mission or start a new one."""
        if os.path.exists(SESSION_FILE):
            resume = input("\nAn existing session file was found. Do you want to resume? (y/n): ").lower()
            if resume != 'y':
                os.remove(SESSION_FILE)
                logging.info("Previous session file deleted. Starting a fresh mission.")

    # --- THE FIX: This method now takes a simple list of IDs and updates the plan ---
    def _update_plan_status(self):
        """Gets completed task IDs from the AI and updates the plan state."""
        logging.info("📝 Assessing plan progress based on recent actions...")
        completed_ids = self.thought_engine.get_completed_task_ids(self.goal, self.plan, self.mission_history)

        if not completed_ids:
            logging.info("  - No new tasks were marked as completed.")
            return

        for task in self.plan:
            if task.task_id in completed_ids and task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.COMPLETED
                logging.info("  - Status Updated: Task %d is now COMPLETED.", task.task_id)

    # ... ( _save_state and _load_state are unchanged) ...
    def _save_state(self):
        state = {"goal": self.goal, "plan": [task.model_dump() for task in self.plan],
                 "mission_history": self.mission_history}
        with open(SESSION_FILE, 'w', encoding='utf-8') as f: json.dump(state, f, indent=4)
        logging.info("Mission state saved to session file.")

    def _load_state(self):
        if not os.path.exists(SESSION_FILE): return False
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            if state.get("goal") != self.goal:
                logging.warning("Session file goal does not match. Starting fresh.")
                os.remove(SESSION_FILE)
                return False
            self.plan = [TaskNode(**task_data) for task_data in state.get("plan", [])]
            self.mission_history = state.get("mission_history", [])
            logging.info("Successfully loaded and resumed mission.")
            return True
        except (json.JSONDecodeError, TypeError) as e:
            logging.error("Failed to load session file. Starting fresh.", e)
            return False

    def run(self):
        """Executes the main Plan -> Execute loop for the agent's mission."""
        if not self._load_state():
            # PLANNING PHASE
            logging.info("Starting new mission for goal: %s", self.goal)
            try:
                self.plan = self.scheduler.create_plan(self.goal)
                if not self.plan:
                    logging.error("Mission aborted: Agent failed to generate a valid plan.");
                    return
                logging.info("High-Level Plan Created:")
                for task in self.plan: logging.info("  %d. %s", task.task_id, task.description)
                if input("\nProceed with this plan? (y/n): ").lower() != 'y':
                    logging.info("Mission aborted by user.");
                    return
                self._save_state()
            except (APITimeoutError, KeyboardInterrupt) as e:
                logging.error("Mission aborted during planning phase: %s", e);
                return

        # EXECUTION LOOP
        try:
            while True:
                action = self.thought_engine.choose_next_action(self.goal, self.plan, self.mission_history)
                if action.tool_name == "finish_mission":
                    logging.info("AI has decided the mission is complete.");
                    self.mission_history.append({"command": "finish_mission", "observation": action.tool_input});
                    break

                filename, file_content = self.mcp_client.execute_command(action.tool_input)
                observation = file_content or f"Command '{action.tool_input}' produced no output."
                if filename:
                    local_filepath = os.path.join(PROJECTS_DIR, filename)
                    with open(local_filepath, 'w', encoding='utf-8') as f:
                        f.write(observation)
                    logging.info("Observation saved to '%s'", local_filepath)
                else:
                    logging.error("Command execution failed: %s", observation)

                self.mission_history.append({"command": action.tool_input, "observation": observation})
                self._update_plan_status()
                self._save_state()

                if len(self.mission_history) >= 20: logging.warning("Max step limit (20) reached."); break
        except (APITimeoutError, KeyboardInterrupt) as e:
            logging.error("Mission aborted during execution loop: %s", e)
        finally:
            self._generate_final_report()
            if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE); logging.info("Session file cleaned up.")

    def _generate_final_report(self):
        logging.info("Generating final mission report...")
        if not self.mission_history: logging.warning("No actions were taken, cannot generate a report."); return
        create_report(self.goal, self.mission_history)