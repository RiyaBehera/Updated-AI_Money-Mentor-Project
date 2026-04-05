def clamp(value: float, minimum: float, maximum: float) -> float:
  return min(maximum, max(minimum, value))


def required_sip(target: float, current: float, annual_rate: float, years: float) -> float:
  monthly_rate = annual_rate / 12 / 100
  months = max(int(years * 12), 1)

  grown_current = current * ((1 + monthly_rate) ** months)
  gap = max(target - grown_current, 0)

  if monthly_rate == 0:
    return gap / months

  multiplier = (((1 + monthly_rate) ** months) - 1) / monthly_rate
  return gap / (multiplier * (1 + monthly_rate))


def rupees(value: float) -> str:
  return f"Rs. {value:,.0f}"
