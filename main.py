# dawnyawn/main.py (Final Version with Resume Logic)
import os
import argparse
import logging
from dotenv import load_dotenv
from agent.task_manager import TaskManager

def setup_logging():
    project_root = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_filepath = os.path.join(logs_dir, 'agent_run.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_filepath, mode='w'), # 'w' for overwrite on new run
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    load_dotenv()
    if not os.getenv("OLLAMA_BASE_URL") or not os.getenv("LLM_MODEL"):
        logging.critical("FATAL ERROR: OLLAMA_BASE_URL or LLM_MODEL not found in .env file.")
        return

    parser = argparse.ArgumentParser(description="DawnYawn Autonomous Agent")
    parser.add_argument("goal", type=str, help="The high-level goal for the agent.")
    args = parser.parse_args()

    logging.info("--- DawnYawn Agent Initializing ---")
    logging.info("--- Using Local LLM: %s ---", os.getenv("LLM_MODEL"))
    logging.warning("SECURITY WARNING: This agent executes AI-generated commands on a remote server.")

    try:
        task_manager = TaskManager(goal=args.goal)
        # --- THE FIX: Ask the user if they want to resume or start fresh ---
        task_manager.initialize_mission()
        task_manager.run()
        logging.info("--- Mission Concluded ---")
    except Exception as e:
        logging.critical("An unhandled exception occurred during the mission: %s", e, exc_info=True)

if __name__ == "__main__":
    main()