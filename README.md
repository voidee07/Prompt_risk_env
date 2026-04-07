---
title: Prompt Risk Env
emoji: 🔒
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
tags:
  - openenv
---



# Prompt Risk Assessment Environment

## What This Is
An OpenEnv environment that simulates enterprise Data Loss Prevention (DLP).
An AI agent analyzes employee prompts sent to LLMs and classifies them by
risk level, sensitive data types, and recommended action.

## Why It Matters
Every company deploying LLMs to employees faces data leakage risk.
Microsoft and Google have billion dollar products solving this exact problem.
There is no standard benchmark to measure how well AI systems detect
sensitive information in prompts. This environment fills that gap.

Real compliance frameworks this addresses:
- GDPR (personal data protection)
- HIPAA (medical data)
- PCI DSS (financial data)

## Environment Description
The agent receives an employee prompt and must classify:
- Risk level: safe / low / medium / high / critical
- Data types present: PII, financial, medical, credentials, confidential_business, legal
- Recommended action: allow / warn / block / escalate

## Observation Space
| Field | Type | Description |
|-------|------|-------------|
| prompt | string | Employee prompt to classify |
| task_id | integer | Task number (1, 2, or 3) |
| task_name | string | easy, medium, or hard |
| step | integer | Current step number |

## Action Space
| Field | Type | Values |
|-------|------|--------|
| risk_level | string | safe, low, medium, high, critical |
| data_types | list | PII, financial, medical, credentials, confidential_business, legal |
| recommended_action | string | allow, warn, block, escalate |

## Tasks

### Task 1 — Easy (12 prompts)
Detect obvious PII like SSNs, credit cards, passport numbers.
Expected difficulty: Low. Even weak models should score above 0.6.

### Task 2 — Medium (16 prompts)
Classify prompts containing multiple sensitive data types simultaneously.
Requires identifying combinations of PII, financial, and medical data.

### Task 3 — Hard (13 prompts)
Detect subtle confidentiality breaches with no obvious PII.
Requires understanding business context and implicit sensitivity.

## Reward Function
Composite score per step:
- 40% — Risk level accuracy (partial credit for adjacent levels)
- 40% — Data types F1 score (precision + recall)
- 20% — Recommended action accuracy
- -0.3 penalty for missing critical risk as safe/low

Final episode score = average reward across all steps.

## Setup Instructions

### Local
```bash
git clone https://github.com/Voidee07/prompt_risk_env
cd prompt_risk_env
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn server.app:app --reload --port 8000
```

### Docker
```bash
docker build -t prompt-risk-env .
docker run -p 8000:7860 prompt-risk-env
```

### Run Inference
```bash
cp .env.example .env
# Add your HF token to .env
python inference.py
```

## Baseline Scores
Evaluated using Qwen/Qwen2.5-72B-Instruct via HuggingFace router.

| Task | Description | Score |
|------|-------------|-------|
| Easy | Obvious PII detection | 0.725 |
| Medium | Multi-label classification | 0.651 |
| Hard | Subtle confidentiality | 0.308 |
| **Overall** | **Average** | **0.561** |

## Environment URL
https://huggingface.co/spaces/Voidee07/prompt_risk_env