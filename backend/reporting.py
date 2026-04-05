from datetime import datetime


def build_plan_report(response: dict) -> str:
  overview = response["overview"]
  fire = response["fire"]
  health = response["health"]
  life_event = response["life_event"]
  tax = response["tax"]
  couple = response["couple"]
  portfolio = response["portfolio"]

  lines = [
    "AI MONEY MENTOR - DOWNLOADABLE PLAN REPORT",
    f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "TOPLINE SUMMARY",
    f"Title: {_stringify_item(overview.get('title', ''))}",
    f"Summary: {_stringify_item(overview.get('summary', ''))}",
    "",
    "KEY METRICS",
    f"Money Health Score: {_stringify_item(health.get('score', 0))}/100",
    f"Required SIP: Rs. {float(fire.get('monthly_sip', 0) or 0):,.0f}",
    f"Emergency Target: Rs. {float(fire.get('emergency_target', 0) or 0):,.0f}",
    f"Insurance Gap: Rs. {float(fire.get('insurance_gap', 0) or 0):,.0f}",
    f"Tax Savings Opportunity: Rs. {float(tax.get('estimated_tax_saved', 0) or 0):,.0f}",
    "",
    "PRIORITY ACTIONS",
  ]

  lines.extend([f"- {_stringify_item(item)}" for item in overview.get("priority_actions", [])])
  lines.extend(["", "FIRE PATH PLANNER", _stringify_item(fire.get("summary", "")), "Roadmap:"])
  lines.extend([f"- {_stringify_item(item)}" for item in fire.get("monthly_roadmap", [])])
  lines.extend(["", "MONEY HEALTH SCORE", _stringify_item(health.get("summary", ""))])
  lines.extend([f"- {_stringify_item(item)}" for item in health.get("focus_actions", [])])
  lines.extend(["", "LIFE EVENT ADVISOR", _stringify_item(life_event.get("summary", ""))])
  lines.extend([f"- {_stringify_item(item)}" for item in life_event.get("actions", [])])
  lines.extend([
    "",
    "TAX WIZARD",
    _stringify_item(tax.get("summary", "")),
    f"Old Regime Tax: Rs. {float(tax.get('old_regime_tax', 0) or 0):,.0f}",
    f"New Regime Tax: Rs. {float(tax.get('new_regime_tax', 0) or 0):,.0f}",
    f"Recommended Regime: {_stringify_item(tax.get('recommended_regime', ''))}",
  ])
  lines.extend([f"- {_stringify_item(item)}" for item in tax.get("actions", [])])
  lines.extend(["", "COUPLE'S MONEY PLANNER", _stringify_item(couple.get("summary", ""))])
  lines.extend([f"- {_stringify_item(item)}" for item in couple.get("actions", [])])
  lines.extend([
    "",
    "MF PORTFOLIO X-RAY",
    _stringify_item(portfolio.get("summary", "")),
    f"Overlap Risk: {_stringify_item(portfolio.get('overlap_risk', ''))}",
    f"Expense Drag: Rs. {float(portfolio.get('expense_drag', 0) or 0):,.0f}",
    f"Benchmark Spread: {_stringify_item(portfolio.get('benchmark_spread', 0))}%",
  ])
  lines.extend([f"- {_stringify_item(item)}" for item in portfolio.get("actions", [])])

  return "\n".join(_stringify_item(line) for line in lines)


def _stringify_item(item) -> str:
  if isinstance(item, dict):
    if "title" in item and "detail" in item:
      return f"{item['title']}: {item['detail']}"
    if "label" in item and "value" in item:
      return f"{item['label']}: {item['value']}"
    return ", ".join(f"{key}: {value}" for key, value in item.items())

  if isinstance(item, list):
    return ", ".join(_stringify_item(value) for value in item)

  return str(item)
