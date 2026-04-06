from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Action, StepResult
from environment import PromptRiskEnvironment

app = FastAPI(
    title="Prompt Risk Assessment Environment",
    description="OpenEnv environment for classifying risk in employee LLM prompts",
    version="1.0.0"
)

# One global environment instance (the server holds state)
env = PromptRiskEnvironment()


# Request body for /reset
class ResetRequest(BaseModel):
    task_id: Optional[int] = 1  # defaults to easy if not specified


@app.post("/reset")
def reset(request: ResetRequest = ResetRequest()):
    try:
        result = env.reset(task_id=request.task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(action: Action):
    try:
        result = env.step(action)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    return env.state()


# Health check — validators ping this
@app.get("/")
def root():
    return {"status": "ok", "environment": "prompt-risk-env"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()