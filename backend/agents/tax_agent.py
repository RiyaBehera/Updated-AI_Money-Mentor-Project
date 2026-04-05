def _apply_slabs(taxable_income, slabs):
  tax = 0.0
  previous_limit = 0.0

  for upper_limit, rate in slabs:
    if taxable_income <= previous_limit:
      break

    slab_income = min(taxable_income, upper_limit) - previous_limit
    if slab_income > 0:
      tax += slab_income * rate
    previous_limit = upper_limit

  if taxable_income > slabs[-1][0]:
    tax += (taxable_income - slabs[-1][0]) * slabs[-1][1]

  return tax


def _old_regime_tax(annual_salary, deductions):
  taxable_income = max(annual_salary - 50000 - deductions, 0)
  slabs = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
  ]
  base_tax = _apply_slabs(taxable_income, slabs)
  if taxable_income <= 500000:
    base_tax = max(base_tax - 12500, 0)
  return round(base_tax * 1.04), round(taxable_income)


def _new_regime_tax(annual_salary):
  taxable_income = max(annual_salary - 75000, 0)
  slabs = [
    (400000, 0.00),
    (800000, 0.05),
    (1200000, 0.10),
    (1600000, 0.15),
    (2000000, 0.20),
    (2400000, 0.25),
  ]
  base_tax = _apply_slabs(taxable_income, slabs)
  if taxable_income <= 1200000:
    base_tax = max(base_tax - 60000, 0)
  return round(base_tax * 1.04), round(taxable_income)


def run_tax_agent(payload, llm):
  annual_salary = float(payload["annual_salary"])
  declared_deductions = float(payload["declared_deductions"])
  other_deductions = float(payload["other_deductions"])
  tax_savings = float(payload["tax_savings"])
  core_deductions = max(declared_deductions, tax_savings)
  total_deductions = core_deductions + other_deductions

  old_regime_tax, old_regime_taxable = _old_regime_tax(annual_salary, total_deductions)
  new_regime_tax, new_regime_taxable = _new_regime_tax(annual_salary)
  estimated_tax_saved = abs(old_regime_tax - new_regime_tax)
  better_regime = "old" if old_regime_tax < new_regime_tax else "new"

  prompt = f"""
You are the Tax Wizard Agent for an Indian personal finance app.
Return valid JSON with keys "title", "summary", and "actions".
"actions" must be an array of exactly 4 short strings.

Inputs:
- Annual salary: {annual_salary}
- Declared deductions: {declared_deductions}
- Other deductions: {other_deductions}
- Existing tax-saving investments: {tax_savings}
- Preferred regime: {payload["preferred_regime"]}
- Form 16 filename: {payload.get("form16_filename", "")}
- Form 16 text extract: {payload.get("form16_text", "")[:2500]}
- Old regime taxable income: {old_regime_taxable}
- New regime taxable income: {new_regime_taxable}
- Estimated old regime tax with cess: {old_regime_tax}
- Estimated new regime tax with cess: {new_regime_tax}
- Better regime by current numbers: {better_regime}

Give practical India-specific tax suggestions and mention whether old or new regime looks stronger.
"""

  narrative = llm.generate_json(prompt)

  return {
    "title": narrative["title"],
    "summary": narrative["summary"],
    "actions": narrative["actions"],
    "old_regime_tax": old_regime_tax,
    "new_regime_tax": new_regime_tax,
    "estimated_tax_saved": round(estimated_tax_saved),
    "recommended_regime": better_regime,
  }
