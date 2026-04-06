import random
from typing import Optional
from models import Observation, Action, StepResult


#hardcoded  prompts for the environment(dataset)
TASKS = {
    1: {
        "name": "easy",
        "description": "Identify obvious PII in prompts",
        "prompts": [
            {
                "text": "My SSN is 456-78-9012, can you help me fill this government form?",
                "risk_level": "critical",
                "data_types": ["PII"],
                "recommended_action": "block"
            },
            {
                "text": "Please send the report to john.smith@company.com and cc sarah.jones@company.com",
                "risk_level": "high",
                "data_types": ["PII"],
                "recommended_action": "warn"
            },
            {
                "text": "My credit card number is 4532-1234-5678-9012, help me dispute a charge",
                "risk_level": "critical",
                "data_types": ["financial"],
                "recommended_action": "block"
            },
            {
                "text": "Draft a message to our team about the Q3 planning meeting tomorrow",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "My phone number is 9876543210, update it in the system please",
                "risk_level": "high",
                "data_types": ["PII"],
                "recommended_action": "warn"
            },
            {
                "text": "Help me write an email about the new office coffee machine policy",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "My passport number is AB1234567, I need help with the visa form",
                "risk_level": "critical",
                "data_types": ["PII"],
                "recommended_action": "block"
            },
            {
                "text": "Summarize the attached public research paper on climate change",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "My home address is 42 Park Street, Mumbai 400001, update my profile",
                "risk_level": "high",
                "data_types": ["PII"],
                "recommended_action": "warn"
            },
            {
                "text": "Help me debug this Python function that sorts a list",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "My bank account number is 9876543210 IFSC HDFC0001234, transfer 5000",
                "risk_level": "critical",
                "data_types": ["financial"],
                "recommended_action": "block"
            },
            {
                "text": "Write a birthday message for my colleague",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
        ]
    },
    2: {
        "name": "medium",
        "description": "Classify multiple sensitive data types",
        "prompts": [
            {
                "text": "Please help me with patient John Doe, DOB 1985-03-12, diagnosed with Type 2 Diabetes, insurance ID BC789012",
                "risk_level": "critical",
                "data_types": ["PII", "medical"],
                "recommended_action": "block"
            },
            {
                "text": "Draft a contract for client Rajesh Kumar (rajesh@acme.com), deal value $2.3M, renewal March 2025",
                "risk_level": "high",
                "data_types": ["PII", "financial"],
                "recommended_action": "warn"
            },
            {
                "text": "Employee Sarah Chen, salary $120,000, SSN 123-45-6789, performance rating: excellent",
                "risk_level": "critical",
                "data_types": ["PII", "financial"],
                "recommended_action": "block"
            },
            {
                "text": "Summarize our API documentation for external developers",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Patient record: Jane Smith, blood type O+, HIV status positive, doctor: Dr. Mehta (dr.mehta@hospital.com)",
                "risk_level": "critical",
                "data_types": ["PII", "medical"],
                "recommended_action": "block"
            },
            {
                "text": "Legal matter: defendant Michael Brown, case #CV-2024-1234, settlement amount $450,000",
                "risk_level": "high",
                "data_types": ["PII", "financial", "legal"],
                "recommended_action": "warn"
            },
            {
                "text": "Help me prepare slides for our public product launch next week",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Vendor payment: TechCorp Ltd, account 12345678, routing 987654, invoice $89,000 due Friday",
                "risk_level": "critical",
                "data_types": ["financial"],
                "recommended_action": "block"
            },
            {
                "text": "Customer complaint from priya.sharma@gmail.com, order #ORD-789, refund $234.50 requested",
                "risk_level": "high",
                "data_types": ["PII", "financial"],
                "recommended_action": "warn"
            },
            {
                "text": "Write a LinkedIn post announcing our new product feature",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Insurance claim: policy #POL-456789, claimant David Lee (dlee@email.com), accident date 2024-01-15, amount $12,000",
                "risk_level": "critical",
                "data_types": ["PII", "financial", "medical"],
                "recommended_action": "block"
            },
            {
                "text": "Help me write a thank you note to our open source contributors",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Staff meeting notes: discussed Q4 targets, revenue shortfall of $2M, potential layoffs in engineering",
                "risk_level": "high",
                "data_types": ["financial"],
                "recommended_action": "warn"
            },
            {
                "text": "Translate our public FAQ page into Hindi",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Prescription for patient ID P-9823: Metformin 500mg twice daily, Dr. Kapoor license #MH-12345",
                "risk_level": "critical",
                "data_types": ["PII", "medical"],
                "recommended_action": "block"
            },
            {
                "text": "Generate a weekly status update template for our engineering team",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
        ]
    },
    3: {
        "name": "hard",
        "description": "Detect subtle confidentiality breaches",
        "prompts": [
            {
                "text": "Our biggest competitor just lost their CTO. Our board thinks this is a good time to poach their enterprise clients. Draft an outreach strategy.",
                "risk_level": "high",
                "data_types": ["proprietary"],
                "recommended_action": "warn"
            },
            {
                "text": "The acquisition talks with StartupX are going well. They've agreed to $45M. Help me draft the internal announcement for after signing.",
                "risk_level": "critical",
                "data_types": ["proprietary", "financial"],
                "recommended_action": "block"
            },
            {
                "text": "Help me write a Python function to calculate compound interest",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "Our Q3 revenue missed targets by 23%. The board wants a recovery plan before the earnings call. Suggest talking points.",
                "risk_level": "critical",
                "data_types": ["proprietary", "financial"],
                "recommended_action": "block"
            },
            {
                "text": "We're planning to lay off 15% of the workforce next month. Help me draft a compassionate internal memo.",
                "risk_level": "critical",
                "data_types": ["proprietary"],
                "recommended_action": "block"
            },
            {
                "text": "Summarize the key points from last week's all-hands meeting about our new remote work policy",
                "risk_level": "medium",
                "data_types": ["proprietary"],
                "recommended_action": "warn"
            },
            {
                "text": "Our new drug compound shows 94% efficacy in phase 2 trials. Help me prepare the investor briefing before FDA submission.",
                "risk_level": "critical",
                "data_types": ["proprietary", "medical"],
                "recommended_action": "block"
            },
            {
                "text": "What is the capital of France?",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "We just got tipped off that a competitor is about to announce a product very similar to ours. Should we accelerate our launch date?",
                "risk_level": "high",
                "data_types": ["proprietary"],
                "recommended_action": "warn"
            },
            {
                "text": "Our internal audit found compliance gaps in 3 regional offices. Help me draft the remediation plan before regulators find out.",
                "risk_level": "critical",
                "data_types": ["proprietary", "legal"],
                "recommended_action": "block"
            },
            {
                "text": "Help me explain recursion to a junior developer using a simple example",
                "risk_level": "safe",
                "data_types": [],
                "recommended_action": "allow"
            },
            {
                "text": "The partnership deal with GlobalBank is contingent on us hitting $10M ARR by December. We're currently at $7.2M. Draft a progress update.",
                "risk_level": "high",
                "data_types": ["proprietary", "financial"],
                "recommended_action": "warn"
            },
        ]
    }
}
#grading scheme for evaluating the agent's actions
def grade_action(action: Action, ground_truth: dict) -> float:
    score = 0.0

    # Part 1: Risk level (40%)
    if action.risk_level == ground_truth["risk_level"]:
        score += 0.4
    elif is_adjacent_risk(action.risk_level, ground_truth["risk_level"]):
        score += 0.2

    # Part 2: Data types (40%)
    predicted = set(action.data_types)
    actual = set(ground_truth["data_types"])

    if actual:
        true_positives = len(predicted & actual)
        precision = true_positives / len(predicted) if predicted else 0
        recall = true_positives / len(actual)
        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
            score += 0.4 * f1
    else:
        if not predicted:
            score += 0.4

    # Part 3: Recommended action (20%)
    if action.recommended_action == ground_truth["recommended_action"]:
        score += 0.2

    # Penalty: missing critical PII is dangerous
    if ground_truth["risk_level"] == "critical" and \
       action.risk_level in ["low", "safe"]:
        score -= 0.3

    return round(max(0.0, min(1.0, score)), 2)


def is_adjacent_risk(predicted: str, actual: str) -> bool:
    risk_order = ["safe", "low", "medium", "high", "critical"]
    if predicted not in risk_order or actual not in risk_order:
        return False
    return abs(risk_order.index(predicted) - risk_order.index(actual)) == 1