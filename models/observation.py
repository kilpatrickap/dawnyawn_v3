# dawnyawn/models/observation.py
from pydantic import BaseModel, Field
from typing import Optional

class Observation(BaseModel):
    """
    A structured representation of the key findings from a tool's output.
    """
    status: str = Field(..., description="The outcome of the command. Either 'SUCCESS' or 'FAILURE'.")
    key_finding: str = Field(..., description="A concise, one-sentence summary of the most important information or error message from the output.")
    full_output_truncated: Optional[bool] = Field(False, description="True if the full_output was too long and has been truncated.")
    full_output: str = Field(..., description="The raw, multi-line output from the command. Truncated if too long.")