import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file first, before anything else
load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN", "")
ENV_URL      = os.getenv("ENV_URL", "http://localhost:8000")

TASKS             = [1, 2, 3]
MAX_STEPS         = 20
SUCCESS_THRESHOLD = 0.5

# This creates the GPT client using your HF token
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# ─── Logging (mandatory format from problem statement) ────────────────────────
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={error_val}",
        flush=True
    )

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True
    )

# ─── System Prompt for GPT ────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an enterprise data loss prevention (DLP) classifier.
You will receive an employee prompt that was sent to an LLM.
Classify it by responding in this EXACT JSON format with no extra text:

{
  "risk_level": "safe|low|medium|high|critical",
  "data_types": ["PII", "financial", "medical", "credentials", "confidential_business", "legal"],
  "recommended_action": "allow|warn|block|escalate"
}

Rules:
- risk_level must be exactly one of: safe, low, medium, high, critical
- data_types must be a list, use [] if none apply
- recommended_action must be exactly one of: allow, warn, block, escalate
- Return ONLY the JSON object, nothing else, no explanation, no markdown
"""

# ─── GPT Classifier ───────────────────────────────────────────────────────────
def classify_prompt(prompt_text: str) -> dict:
    """
    Sends the employee prompt to GPT.
    Gets back risk_level, data_types, recommended_action.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Classify this prompt:\n\n{prompt_text}"}
            ],
            temperature=0.0,  # must be 0 for reproducible scores
            max_tokens=150,
        )

        raw = response.choices[0].message.content.strip()

        # Sometimes GPT wraps response in ```json ... ```
        # This strips those out
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        raw = raw.strip()
        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parse error: {e} | raw: {raw}", flush=True)
        # Safe fallback — episode continues even if GPT gives bad output
        return {
            "risk_level": "medium",
            "data_types": [],
            "recommended_action": "warn"
        }
    except Exception as e:
        print(f"[DEBUG] GPT call failed: {e}", flush=True)
        return {
            "risk_level": "medium",
            "data_types": [],
            "recommended_action": "warn"
        }

# ─── Run One Full Task Episode ────────────────────────────────────────────────
def run_task(task_id: int) -> float:
    """
    Runs one complete task (all prompts).
    Returns average score for that task.
    """
    task_name = {1: "easy", 2: "medium", 3: "hard"}[task_id]

    log_start(task=task_name, env="prompt-risk-env", model=MODEL_NAME)

    rewards     = []
    steps_taken = 0
    score       = 0.0
    success     = False

    try:
        # ── Step 1: Reset environment for this task ──
        reset_response = requests.post(
            f"{ENV_URL}/reset",
            json={"task_id": task_id}
        )
        result = reset_response.json()
        done   = result.get("done", False)

        # ── Step 2: Loop through all prompts in task ──
        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            # Get the current prompt from observation
            obs = result.get("observation")
            if obs is None:
                break

            prompt_text = obs["prompt"]

            # Ask GPT to classify the prompt
            classification = classify_prompt(prompt_text)

            # Send classification to /step as an action
            step_response = requests.post(
                f"{ENV_URL}/step",
                json=classification
            )
            result = step_response.json()

            reward = result.get("reward", 0.0)
            done   = result.get("done", False)
            error  = result.get("info", {}).get("error", None)

            rewards.append(reward)
            steps_taken = step

            # Compact action string for the log
            action_str = (
                f"risk={classification['risk_level']},"
                f"types={classification['data_types']},"
                f"action={classification['recommended_action']}"
            )

            log_step(
                step=step,
                action=action_str,
                reward=reward,
                done=done,
                error=error
            )

        # ── Step 3: Calculate final score ──
        score   = sum(rewards) / len(rewards) if rewards else 0.0
        score   = round(min(max(score, 0.0), 1.0), 3)
        success = score >= SUCCESS_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Task {task_id} crashed: {e}", flush=True)
        score = 0.0

    finally:
        log_end(
            success=success,
            steps=steps_taken,
            score=score,
            rewards=rewards
        )

    return score

# ─── Main Entry Point ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Sanity check before running
    if not HF_TOKEN:
        print("[DEBUG] WARNING: HF_TOKEN is empty. GPT calls will fail.", flush=True)

    print(f"[DEBUG] Server: {ENV_URL}", flush=True)
    print(f"[DEBUG] Model:  {MODEL_NAME}", flush=True)
    print(f"[DEBUG] Tasks:  {TASKS}", flush=True)
    print("", flush=True)

    all_scores = []

    for task_id in TASKS:
        score = run_task(task_id)
        all_scores.append(score)
        print(f"[DEBUG] Task {task_id} score: {score:.3f}", flush=True)
        print("", flush=True)  # blank line between tasks for readability

    overall = sum(all_scores) / len(all_scores)
    print(f"[DEBUG] Overall score across all tasks: {overall:.3f}", flush=True)