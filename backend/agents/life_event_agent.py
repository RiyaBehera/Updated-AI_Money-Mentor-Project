def run_life_event_agent(payload, llm):
  prompt = f"""
You are the Life Event Agent for an Indian AI finance mentor.
Return valid JSON with keys "title", "summary", and "actions".
"actions" must be an array of exactly 4 short strings.

User data:
- Life event: {payload["life_event"]}
- Event amount: {payload["event_amount"]}
- Risk profile: {payload["risk_profile"]}
- Tax bracket: {payload["tax_bracket"]}
- Monthly income: {payload["monthly_income"]}
- Monthly expenses: {payload["monthly_expenses"]}
- Debt outstanding: {payload["debt_outstanding"]}
- Emergency fund: {payload["emergency_fund"]}
- Primary goal: {payload["primary_goal"]}

Make the advice personalised and practical.
"""

  narrative = llm.generate_json(prompt)

  return {
    "title": narrative["title"],
    "summary": narrative["summary"],
    "actions": narrative["actions"],
  }
