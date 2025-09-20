# dawnyawn/reporting/report_generator.py (Corrected for String Observation)
import os
import logging
from datetime import datetime
from typing import List, Dict

# Define the project root relative to this file's location
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Correctly point to the Reports directory inside the Projects folder
REPORTS_DIR = os.path.join(PROJECT_ROOT, "Projects", "Reports")


def create_report(goal: str, history: List[Dict]):
    """Generates a professional text report from the mission history."""
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.txt"
        report_filepath = os.path.join(REPORTS_DIR, report_filename)

        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write("--- DAWNYAWN MISSION REPORT ---\n")
            f.write("=" * 35 + "\n\n")
            f.write(f"Mission Goal: {goal}\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("--- EXECUTION LOG ---\n")
            f.write("=" * 21 + "\n\n")

            if not history:
                f.write("No actions were executed during this mission.\n")
            else:
                for i, item in enumerate(history):
                    f.write(f"Step {i + 1}:\n")
                    f.write("-" * 10 + "\n")
                    f.write(f"  Action Command:\n    `{item.get('command', 'N/A')}`\n\n")
                    f.write("  Observation:\n")

                    obs_text = item.get('observation', 'No observation recorded.')
                    if not isinstance(obs_text, str):
                        obs_text = str(obs_text)

                    indented_obs = "    " + obs_text.replace('\n', '\n    ')
                    f.write(indented_obs)
                    f.write("\n\n")

            f.write("--- FINAL SUMMARY ---\n")
            f.write("=" * 21 + "\n\n")

            # --- THE FIX: Handle both string and dict observations for the final step ---
            final_finding = "Mission did not conclude with a `finish_mission` command."
            if history and history[-1].get('command') == 'finish_mission':
                final_observation = history[-1].get('observation')
                # If the observation is a simple string (from a failure), just use it.
                if isinstance(final_observation, str):
                    final_finding = final_observation
                # If it's a dictionary (from a successful finish), get the key_finding.
                elif isinstance(final_observation, dict):
                    final_finding = final_observation.get('key_finding', "No summary provided.")

            f.write(f"{final_finding}\n")

        logging.info("✅ Professional report generated at: %s", report_filepath)

    except IOError as e:
        logging.error("Failed to write report file: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred during report generation: %s", e, exc_info=True)