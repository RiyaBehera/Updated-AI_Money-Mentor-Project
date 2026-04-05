def run_portfolio_agent(payload, llm):
  equity_allocation = float(payload["equity_allocation"])
  alt_allocation = float(payload["alt_allocation"])
  expense_ratio = float(payload["expense_ratio"])
  xirr = float(payload["portfolio_xirr"])
  benchmark = float(payload["benchmark_return"])
  investments = float(payload["existing_investments"])

  benchmark_spread = round(xirr - benchmark, 1)
  expense_drag = round(investments * (expense_ratio / 100))
  fund_count = float(payload["fund_count"])

  if equity_allocation > 82:
    overlap_risk = "High"
  elif equity_allocation > 68:
    overlap_risk = "Moderate"
  else:
    overlap_risk = "Low"

  prompt = f"""
You are the Portfolio X-Ray Agent for an Indian finance product.
Return valid JSON with keys "title", "summary" and "actions".
"actions" must be an array of exactly 4 short strings.

Portfolio data:
- Equity allocation: {equity_allocation}
- Alternative allocation: {alt_allocation}
- Expense ratio: {expense_ratio}
- XIRR: {xirr}
- Benchmark return: {benchmark}
- Benchmark spread: {benchmark_spread}
- Expense drag: {expense_drag}
- Overlap risk: {overlap_risk}
- Number of funds: {fund_count}
- Statement filename: {payload.get("portfolio_statement_filename", "")}
- Statement text extract: {payload.get("portfolio_statement_text", "")[:2500]}

Focus on diversification, fees, and rebalancing clarity.
"""

  narrative = llm.generate_json(prompt)

  return {
    "title": narrative["title"],
    "summary": narrative["summary"],
    "actions": narrative["actions"],
    "overlap_risk": overlap_risk,
    "expense_drag": expense_drag,
    "benchmark_spread": benchmark_spread,
  }
