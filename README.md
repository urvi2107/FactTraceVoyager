# 🏛️ Claim Verification Debate System

A multi-agent AI debate system that evaluates whether external claims faithfully represent source facts. Uses adversarial AI agents with distinct personalities to simulate a courtroom-style debate.

## 🎯 Purpose

Given a pair of statements:
- **Internal Fact**: A source truth (e.g., a specific statistic from a report)
- **External Claim**: A statement derived from that fact (e.g., a tweet, headline, or summary)

The system determines: **Is the external claim a faithful representation of the internal fact — or is it a mutation?**

## 🤖 The Agents

| Agent | Role | Personality |
|-------|------|-------------|
| **Sceptic** | Prosecutor | Ruthless attacker. Hunts for counter-evidence, cherry-picking, and numerical discrepancies. Never concedes a point. |
| **Defender** | Defense Attorney | Protects the claim. Argues that simplification ≠ distortion. Reframes attacks as pedantry. |
| **Fact-Checker** | Neutral Verifier | No allegiance. Extracts specific disputed facts and compares them directly to the source. Calls out both sides. |
| **Mediator** | Diplomat | Finds common ground. Identifies what both sides agree on and proposes compromise resolutions. |
| **Jury** | Final Judge | Weighs all arguments and delivers a structured verdict with confidence scores. |

## 📊 Evaluation Dimensions

The Jury evaluates claims on three dimensions:

1. **Factual Correctness** (0-100%): Are the core facts accurate?
2. **Temporal Accuracy** (0-100%): Are dates, timelines, and sequences correct?
3. **Completeness** (0-100%): Does the claim include necessary context?

Final verdict: `FAITHFUL` | `PARTIALLY FAITHFUL` | `MUTATION`
