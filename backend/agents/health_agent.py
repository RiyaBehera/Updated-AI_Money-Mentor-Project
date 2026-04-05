from agents.helpers import clamp, rupees


def run_health_agent(payload, llm):
  income = float(payload["monthly_income"])
  expenses = float(payload["monthly_expenses"])
  emergency_fund = float(payload["emergency_fund"])
  insurance_cover = float(payload["insurance_cover"])
  debt = float(payload["debt_outstanding"])
  tax_savings = float(payload["tax_savings"])
  retirement_corpus = float(payload["retirement_corpus"])
  equity_allocation = float(payload["equity_allocation"])
  alt_allocation = float(payload["alt_allocation"])

  emergency_months = emergency_fund / expenses if expenses else 0
  recommended_insurance = income * 12 * 15
  emergency_score = clamp((emergency_months / 6) * 100, 0, 100)
  insurance_score = clamp((insurance_cover / max(recommended_insurance, 1)) * 100, 0, 100)
  debt_score = clamp(100 - ((debt / max(income * 12, 1)) * 80), 10, 100)
  diversification_score = clamp(100 - abs(equity_allocation - 65) * 1.4 - abs(alt_allocation - 15) * 1.8, 20, 100)
  tax_score = clamp((tax_savings / 150000) * 100, 15, 100)
  retirement_target = income * 12 * 2.5
  retirement_score = clamp((retirement_corpus / max(retirement_target, 1)) * 100, 10, 100)
  score = round(
    (
      emergency_score
      + insurance_score
      + debt_score
      + diversification_score
      + tax_score
      + retirement_score
    ) / 6
  )

  metrics = {
    "emergency_months": round(emergency_months, 1),
    "recommended_insurance": round(recommended_insurance),
    "component_scores": {
      "emergency": round(emergency_score),
      "insurance": round(insurance_score),
      "debt": round(debt_score),
      "diversification": round(diversification_score),
      "tax": round(tax_score),
      "retirement": round(retirement_score),
    },
  }

  prompt = f"""
You are the Money Health Agent for an Indian personal finance app.
Return valid JSON with keys "headline", "summary", and "focus_actions".
The "focus_actions" value must be an array of exactly 3 short strings.

User data:
- Monthly income: {income}
- Monthly expenses: {expenses}
- Emergency fund months: {metrics["emergency_months"]}
- Insurance cover: {insurance_cover}
- Recommended insurance: {metrics["recommended_insurance"]}
- Debt outstanding: {debt}
- Tax savings: {tax_savings}
- Retirement corpus: {retirement_corpus}
- Equity allocation: {equity_allocation}
- Alternative allocation: {alt_allocation}
- Overall score: {score}

Be practical, India-specific, and avoid legal disclaimers.
"""

  narrative = llm.generate_json(prompt)

  return {
    "score": score,
    "headline": narrative["headline"],
    "summary": narrative["summary"],
    "focus_actions": narrative["focus_actions"],
    "metrics": metrics,
  }
