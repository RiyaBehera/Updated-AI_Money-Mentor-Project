def run_couple_agent(payload, llm):
  your_income = float(payload["your_monthly_income"])
  partner_income = float(payload["partner_monthly_income"])
  household_expenses = float(payload["household_expenses"])
  combined_investments = float(payload["combined_investments"])
  combined_insurance = float(payload["combined_insurance"])
  combined_monthly_surplus = max(your_income + partner_income - household_expenses, 0)

  prompt = f"""
You are the Couple's Money Planner Agent for an Indian finance app.
Return valid JSON with keys "title", "summary", and "actions".
"actions" must be an array of exactly 4 short strings.

Inputs:
- Your monthly income: {your_income}
- Partner monthly income: {partner_income}
- Household monthly expenses: {household_expenses}
- Combined monthly surplus: {combined_monthly_surplus}
- Combined investments: {combined_investments}
- Combined insurance cover: {combined_insurance}
- Housing status: {payload["housing_status"]}
- Primary goal: {payload["primary_goal"]}

Give advice on SIP split, tax optimisation, insurance responsibility, and joint planning.
"""

  narrative = llm.generate_json(prompt)

  return {
    "title": narrative["title"],
    "summary": narrative["summary"],
    "actions": narrative["actions"],
    "combined_monthly_surplus": round(combined_monthly_surplus),
  }
