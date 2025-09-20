# dawnyawn/services/event_manager.py
from models.task_node import TaskNode


class EventManager:
    """A simple alert and logging system. In a real system, this would
    connect to DingTalk, Slack, or a dedicated logging service."""

    def log_event(self, level: str, message: str):
        """Logs a general system event."""
        print(f"[{level}] {message}")

    def log_task_status(self, task: TaskNode):
        """Logs the current status of a specific task."""
        print(f"[{task.status}] Task {task.task_id}: {task.description}")