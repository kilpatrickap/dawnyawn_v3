# dawnyawn/models/task_node.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskNode(BaseModel):
    """Represents a single execution unit or step in a plan."""
    task_id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    tool_used: Optional[str] = None
    tool_input: Optional[str] = None
    raw_result: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        use_enum_values = True