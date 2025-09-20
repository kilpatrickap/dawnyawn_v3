# dawnyawn/tests/test_agent_scheduler.py (NEW FILE)
import pytest
from agent.agent_scheduler import AgentScheduler

# A sample text response from a mocked LLM
MOCK_LLM_RESPONSE = """
Here is the plan you requested:
1. First step of the plan.
2. Second step, which is also important.
3. The final third step.
Thank you for using my services.
"""

def test_parse_plan_from_text():
    """
    Tests that the _parse_plan_from_text method correctly extracts
    a numbered list from a larger text block.
    """
    scheduler = AgentScheduler()
    # Access the "private" method for unit testing
    parsed_steps = scheduler._parse_plan_from_text(MOCK_LLM_RESPONSE)

    assert len(parsed_steps) == 3
    assert parsed_steps[0] == "First step of the plan."
    assert parsed_steps[1] == "Second step, which is also important."
    assert parsed_steps[2] == "The final third step."

# To run tests:
# 1. Run from the project root directory: pytest