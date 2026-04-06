
from pydantic import BaseModel
from typing import List, Optional, Literal, get_args 

# Valid labels the agent must choose from
VALID_DATA_TYPES = [
    "PII", "financial", "medical", "credentials",
    "confidential_business", "legal", "none"
]

VALID_RISK_LEVELS = ["safe", "low", "medium", "high", "critical"]
VALID_ACTIONS = ["allow", "warn", "block", "escalate"]


class Observation(BaseModel):
    prompt: str        # The employee prompt to classify
    task_id: int       # 1=easy, 2=medium, 3=hard
    task_name: str     # Human readable task name
    step: int          # Which prompt we're on (1-based)


class Action(BaseModel):
    risk_level: Literal["safe", "low", "medium", "high", "critical"]
    data_types: List[str]   # Subset of VALID_DATA_TYPES
    recommended_action: Literal["allow", "warn", "block", "escalate"]


class StepResult(BaseModel):
    observation: Optional[Observation]  # None when done=True
    reward: float                        # 0.0 to 1.0
    done: bool
    info: dict                           # Extra grader details


class State(BaseModel):
    current_index: int   # Which prompt we're on internally
    task_id: int
    done: bool
    steps_taken: int