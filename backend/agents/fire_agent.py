from agents.helpers import clamp, required_sip


def run_fire_agent(payload, llm):
  age = float(payload["age"])
  fire_age = float(payload["fire_age"])
  income = float(payload["monthly_income"])
  expenses = float(payload["monthly_expenses"])
  insurance_cover = float(payload["insurance_cover"])
  investments = float(payload["existing_investments"])
  goal_corpus = float(payload["goal_corpus"])
  expected_return = float(payload["expected_return"])
  salary_growth = float(payload["salary_growth"])

  years = max(fire_age - age, 1)
  monthly_sip = round(required_sip(goal_corpus, investments, expected_return, years))
  emergency_target = round(expenses * 6)
  insurance_gap = round(max(income * 12 * 15 - insurance_cover, 0))
  monthly_surplus = round(max(income - expenses, 0))
  early_equity = round(clamp(75 - years * 0.6, 55, 75))
  later_equity = round(clamp(early_equity - 15, 40, 65))
  alt_mix = 15
  debt_mix = max(100 - early_equity - alt_mix, 0)

  projection_points = []
  for marker in [0, max(1, round(years / 3)), max(2, round((years * 2) / 3)), round(years)]:
    projected_value = investments * ((1 + expected_return / 100) ** marker) + (monthly_sip * 12 * marker)
    projection_points.append({
      "label": f"Y{int(marker)}",
      "value": round(projected_value),
    })

  prompt = f"""
You are the FIRE Planning Agent for an Indian finance mentor.
Return valid JSON with keys "summary", "monthly_roadmap", and "allocation_note".
"monthly_roadmap" must be an array of exactly 6 action strings for the next 6 months.

User data:
- Age: {age}
- FIRE age: {fire_age}
- Years left: {years}
- Goal corpus: {goal_corpus}
- Existing investments: {investments}
- Expected return: {expected_return}
- Monthly SIP needed: {monthly_sip}
- Monthly surplus: {monthly_surplus}
- Emergency target: {emergency_target}
- Insurance gap: {insurance_gap}
- Suggested equity now: {early_equity}
- Suggested equity near FIRE: {later_equity}
- Salary growth: {salary_growth}
- Primary goal: {payload["primary_goal"]}

Tone: direct, motivating, and simple.
"""

  narrative = llm.generate_json(prompt)

  return {
    "headline": "Financial independence roadmap",
    "summary": narrative["summary"],
    "monthly_sip": monthly_sip,
    "emergency_target": emergency_target,
    "insurance_gap": insurance_gap,
    "monthly_surplus": monthly_surplus,
    "monthly_roadmap": narrative["monthly_roadmap"],
    "allocation_note": narrative["allocation_note"],
    "projection_points": projection_points,
    "allocation_mix": {
      "equity": early_equity,
      "debt": debt_mix,
      "alt": alt_mix,
    },
  }
