from pydantic import BaseModel
from typing import List, Optional

class Observation(BaseModel):
    prompt: str
    task_id: int
    task_name: str
    step: int

class Action(BaseModel):
    risk_level: str
    data_types: List[str]
    recommended_action: str

class StepResult(BaseModel):
    observation: Optional[Observation]
    reward: float
    done: bool
    info: dict