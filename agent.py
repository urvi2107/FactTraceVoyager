import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-4.1-mini"
PRICING = (0.40, 1.60)

AGENTS = {
    "Sceptic": """You are a ruthless prosecutor in a courtroom. Your job is to tear this claim apart.

You speak with conviction and authority. You point fingers. You say things like "The claim states X, 
but the evidence CLEARLY shows Y" and "This is a textbook case of cherry-picking."

Instructions:
- Hunt for counter-evidence that destroys the claim.
- Expose alternative interpretations the claim conveniently ignores.
- Call out cherry-picking, scope mismatch, and numerical sleight of hand.
- Treat any uncertainty as reasonable doubt — and doubt means MUTATION.

Focus your attack on THREE dimensions:
1. FACTUAL CORRECTNESS: Are the stated facts wrong?
2. TEMPORAL ACCURACY: Are dates, timelines, or sequences misrepresented?
3. COMPLETENESS: What critical context is conveniently OMITTED?

Rules:
- Never concede a point. Never praise the claim.
- Don't accuse of lying — accuse of being WRONG.
- Quote the specific numbers and dates that don't add up.
- Be sharp, be direct, be relentless. 3-4 sentences max.""",

    "Defender": """You are a high-stakes Defense Attorney. Your client is the 'Claim,'
and you must protect its credibility at all costs.

STANCE:
1. THE SPIRIT OVER THE LETTER: If the numbers aren't exact, argue they represent the 'undeniable trend.'
2. PREVENT HARMFUL PEDANTRY: Attack the Sceptic for 'missing the forest for the trees.'
3. REFRAME MISSTEPS: If a date or figure is slightly off, argue it's a 'necessary simplification.'

You must defend on THREE fronts:
1. FACTUAL CORRECTNESS: The core facts ARE accurate where it matters.
2. TEMPORAL ACCURACY: Timeline simplifications don't change the truth.
3. COMPLETENESS: The claim includes what's RELEVANT, not every tangent.

Your goal is to win. Even if the claim has flaws, focus the Jury on why the core message is FAITHFUL.
Quote the Sceptic only to dismantle their 'narrow-minded' logic. Max 3-4 sentences.""",

    "FactChecker": """You are a Pedantic Fact-Checker. You have NO allegiance to either side.
Your only loyalty is to PRECISION and EVIDENCE.

Your job:
- Extract the SPECIFIC factual claims being disputed (dates, numbers, attributions, causations).
- Compare them DIRECTLY to what the source fact states.
- Call out BOTH sides when they misrepresent or exaggerate.
- Ground the debate in what can actually be verified.

You don't argue. You CLARIFY. You say things like:
- "The fact states X. The claim states Y. These are/are not equivalent."
- "The Sceptic claims Z, but this is not supported by the source material."
- "The Defender's reframing changes the meaning from A to B."

Be precise. Be neutral. Be merciless about accuracy. 2-3 sentences max.""",

    "Mediator": """You are a skilled Mediator. Your job is to find COMMON GROUND between the Sceptic and Defender.

You are NOT here to judge who is right. You are here to:
1. IDENTIFY AGREEMENT: What points do BOTH sides actually agree on (even if they won't admit it)?
2. NARROW THE DISPUTE: Strip away the rhetoric. What is the ACTUAL disagreement about?
3. PROPOSE COMPROMISE: Can the claim be considered "partially faithful"? Under what conditions?

Your tone is calm, diplomatic, and focused on resolution. You say things like:
- "Both sides agree that X. The real dispute is whether Y matters."
- "The Sceptic's concern about Z is valid, but the Defender is correct that W."
- "A fair assessment would acknowledge both A and B."

You push both sides toward a NUANCED conclusion, not absolute victory for either.
Summarize: (1) Points of agreement, (2) Core remaining dispute, (3) Your proposed resolution. 3-5 sentences.""",
}

JURY_PROMPT = """You are an impartial jury deliberating on whether a CLAIM faithfully represents a FACT.

You have heard arguments from:
- A Sceptic (attacking the claim)
- A Defender (supporting the claim)  
- A Fact-Checker (verifying specifics)
- A Mediator (finding common ground)

You must evaluate the claim on THREE specific dimensions and provide a score for each:

1. FACTUAL CORRECTNESS (0-100%): Are the core facts in the claim accurate?
   - Are names, numbers, events correctly stated?
   - Are cause-effect relationships accurate?

2. TEMPORAL ACCURACY (0-100%): Are dates, timelines, and sequences correct?
   - Are specific dates accurate?
   - Is the chronological order of events preserved?
   - Are time-related qualifiers (e.g., "early March") accurate?

3. COMPLETENESS (0-100%): Does the claim include necessary context, or does it mislead through omission?
   - Are critical caveats included?
   - Does omitted information change the meaning?
   - Is the claim misleading even if technically true?

IMPORTANT: Weigh the Mediator's synthesis heavily—they have identified where the parties agree and disagree.

OUTPUT FORMAT (you must follow this exactly):
---
FACTUAL CORRECTNESS: [score]% - [1 sentence explanation]
TEMPORAL ACCURACY: [score]% - [1 sentence explanation]  
COMPLETENESS: [score]% - [1 sentence explanation]

OVERALL VERDICT: [FAITHFUL / PARTIALLY FAITHFUL / MUTATION]
CONFIDENCE: [0-100]%
SUMMARY: [2-3 sentence final judgment weighing all three dimensions]
---"""

client = OpenAI(api_key=api_key)


def get_agent_response(agent_name: str, system_prompt: str, messages: list) -> dict:
    """Get a response from an agent."""
    in_price, out_price = PRICING
    
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + messages,
    )
    elapsed = time.perf_counter() - start
    
    content = response.choices[0].message.content
    usage = response.usage
    cost = (usage.prompt_tokens * in_price + usage.completion_tokens * out_price) / 1_000_000
    
    return {
        "agent": agent_name,
        "content": content,
        "time": elapsed,
        "tokens": usage.total_tokens,
        "cost": cost,
    }


def run_debate(internal_fact: str, external_claim: str):
    """Run a structured debate between agents about claim faithfulness."""
    total_cost = 0
    debate_transcript = []
    
    initial_context = f"""FACT (Source of Truth): 
"{internal_fact}"

CLAIM (To Be Verified): 
"{external_claim}"

Evaluate whether the CLAIM faithfully represents the FACT."""

    print(f"\n{'=' * 70}")
    print("CLAIM VERIFICATION DEBATE")
    print(f"{'=' * 70}")
    print(f"\n📋 FACT:\n{internal_fact}")
    print(f"\n📝 CLAIM:\n{external_claim}")
    print(f"\n{'=' * 70}")
    print("DEBATE (5 rounds)")
    print(f"{'=' * 70}")
    
    # Round 1: Sceptic opens
    print(f"\n--- ROUND 1: SCEPTIC OPENING ---\n")
    sceptic_msg = [{"role": "user", "content": f"{initial_context}\n\nSceptic, present your case against this claim."}]
    s_res = get_agent_response("Sceptic", AGENTS["Sceptic"], sceptic_msg)
    total_cost += s_res["cost"]
    print(s_res["content"])
    print(f"\n[{s_res['time']:.2f}s | {s_res['tokens']} tokens | ${s_res['cost']:.6f}]")
    debate_transcript.append(f"[Sceptic]: {s_res['content']}")
    
    # Round 2: Defender responds
    print(f"\n--- ROUND 2: DEFENDER RESPONSE ---\n")
    defender_msg = [{"role": "user", "content": f"{initial_context}\n\nThe Sceptic argues:\n{s_res['content']}\n\nDefender, respond to these attacks."}]
    d_res = get_agent_response("Defender", AGENTS["Defender"], defender_msg)
    total_cost += d_res["cost"]
    print(d_res["content"])
    print(f"\n[{d_res['time']:.2f}s | {d_res['tokens']} tokens | ${d_res['cost']:.6f}]")
    debate_transcript.append(f"[Defender]: {d_res['content']}")
    
    # Round 3: Fact-Checker grounds the debate
    print(f"\n--- ROUND 3: FACT-CHECKER INTERVENTION ---\n")
    fc_msg = [{"role": "user", "content": f"""{initial_context}

DEBATE SO FAR:
Sceptic: {s_res['content']}
Defender: {d_res['content']}

Fact-Checker, clarify what can actually be verified. Who is misrepresenting the evidence?"""}]
    fc_res = get_agent_response("FactChecker", AGENTS["FactChecker"], fc_msg)
    total_cost += fc_res["cost"]
    print(fc_res["content"])
    print(f"\n[{fc_res['time']:.2f}s | {fc_res['tokens']} tokens | ${fc_res['cost']:.6f}]")
    debate_transcript.append(f"[FactChecker]: {fc_res['content']}")
    
    # Round 4: Mediator finds common ground
    print(f"\n--- ROUND 4: MEDIATOR SYNTHESIS ---\n")
    med_msg = [{"role": "user", "content": f"""{initial_context}

DEBATE SO FAR:
Sceptic: {s_res['content']}
Defender: {d_res['content']}
Fact-Checker: {fc_res['content']}

Mediator, identify the common ground. What do both sides agree on? What is the core remaining dispute? 
Propose a resolution that both sides could accept."""}]
    med_res = get_agent_response("Mediator", AGENTS["Mediator"], med_msg)
    total_cost += med_res["cost"]
    print(med_res["content"])
    print(f"\n[{med_res['time']:.2f}s | {med_res['tokens']} tokens | ${med_res['cost']:.6f}]")
    debate_transcript.append(f"[Mediator]: {med_res['content']}")
    
    # Round 5: Final statements responding to Mediator's synthesis
    print(f"\n--- ROUND 5: FINAL STATEMENTS (responding to Mediator) ---\n")
    
    # Sceptic final - must respond to Mediator's proposed resolution
    s_final_msg = [{"role": "user", "content": f"""{initial_context}

The Mediator proposes: {med_res['content']}

Sceptic, do you accept this resolution? If not, what is the ONE most critical issue that cannot be compromised?
Keep it to 2-3 sentences."""}]
    s_final = get_agent_response("Sceptic", AGENTS["Sceptic"], s_final_msg)
    total_cost += s_final["cost"]
    print(f"[SCEPTIC FINAL]:\n{s_final['content']}")
    print(f"[{s_final['time']:.2f}s | {s_final['tokens']} tokens | ${s_final['cost']:.6f}]\n")
    debate_transcript.append(f"[Sceptic Final]: {s_final['content']}")
    
    # Defender final - must respond to Mediator's proposed resolution
    d_final_msg = [{"role": "user", "content": f"""{initial_context}

The Mediator proposes: {med_res['content']}

Defender, do you accept this resolution? Make your final case for why the claim should be considered faithful.
Keep it to 2-3 sentences."""}]
    d_final = get_agent_response("Defender", AGENTS["Defender"], d_final_msg)
    total_cost += d_final["cost"]
    print(f"[DEFENDER FINAL]:\n{d_final['content']}")
    print(f"[{d_final['time']:.2f}s | {d_final['tokens']} tokens | ${d_final['cost']:.6f}]")
    debate_transcript.append(f"[Defender Final]: {d_final['content']}")
    
    # Jury deliberation
    print(f"\n{'=' * 70}")
    print("⚖️  JURY DELIBERATION")
    print(f"{'=' * 70}\n")
    
    jury_prompt = f"""FACT (Source of Truth): 
"{internal_fact}"

CLAIM (To Be Verified): 
"{external_claim}"

COMPLETE DEBATE TRANSCRIPT:
{chr(10).join(debate_transcript)}

The Mediator's proposed resolution was:
{med_res['content']}

Based on the full debate—especially the Mediator's synthesis and whether the parties accepted it—deliver your verdict on:
FACTUAL CORRECTNESS, TEMPORAL ACCURACY, and COMPLETENESS."""

    j_res = get_agent_response("Jury", JURY_PROMPT, [{"role": "user", "content": jury_prompt}])
    total_cost += j_res["cost"]
    
    print(j_res["content"])
    print(f"\n[{j_res['time']:.2f}s | {j_res['tokens']} tokens | ${j_res['cost']:.6f}]")
    
    print(f"\n{'=' * 70}")
    print(f"💰 TOTAL COST: ${total_cost:.6f}")
    print(f"{'=' * 70}")
    
    return {
        "transcript": debate_transcript,
        "verdict": j_res["content"],
        "total_cost": total_cost
    }


if __name__ == "__main__":
    
    fact = "During the 2020 coronavirus pandemic in the US , a study proving the effectivity hydroxychloroquine to treat this virus was done in a non-randomized group and published on YouTube instead of a peer-reviewed journal ."
    
    claim = "This is in violation of federal law , since none have been determined to be safe and effective by the FDA.In early March President Trump directed the FDA to accelerate the testing and possible use of certain medications to discover if they would help treat patients who already have COVID-19. '' U.S . Moves to Expand Array of Drug Therapies Deployed Against Coronavirus '' , The Wall Street Journal , March 19 , 2020 Among potential drugs are chloroquine and hydroxychloroquine , which have been successfully used to treat malaria ; however , they have never undergone properly designed clinical trials for the treatment of the coronavirus , and the one study reporting positive results was in a small , non-randomized group of patients and was published on YouTube rather than a peer-reviewed journal ."
    
    run_debate(fact, claim)