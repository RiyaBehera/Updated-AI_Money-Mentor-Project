def run_synthesis_agent(payload, health, fire, life_event, tax, couple, portfolio, llm):
  prompt = f"""
You are the Lead Synthesis Agent for an Indian AI finance mentor.
Return valid JSON with keys "title", "summary", and "priority_actions".
"priority_actions" must be an array of exactly 5 concise strings.

User profile:
- Age: {payload["age"]}
- Monthly income: {payload["monthly_income"]}
- Monthly expenses: {payload["monthly_expenses"]}
- Primary goal: {payload["primary_goal"]}
- Risk profile: {payload["risk_profile"]}

Agent outputs:
- Health score: {health["score"]}
- Health summary: {health["summary"]}
- FIRE summary: {fire["summary"]}
- Life event summary: {life_event["summary"]}
- Tax summary: {tax["summary"]}
- Couple summary: {couple["summary"]}
- Portfolio summary: {portfolio["summary"]}
- Monthly SIP: {fire["monthly_sip"]}
- Emergency target: {fire["emergency_target"]}
- Insurance gap: {fire["insurance_gap"]}
- Estimated tax saved: {tax["estimated_tax_saved"]}

Your job is to combine everything into one clear top-level response.
"""

  narrative = llm.generate_json(prompt)

  return {
    "title": narrative["title"],
    "summary": narrative["summary"],
    "priority_actions": narrative["priority_actions"],
  }
