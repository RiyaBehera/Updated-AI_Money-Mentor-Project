import json
import os
import re
from typing import Any

from google import genai
from google.genai import types

from agents.fire_agent import run_fire_agent
from agents.health_agent import run_health_agent
from agents.life_event_agent import run_life_event_agent
from agents.portfolio_agent import run_portfolio_agent
from agents.tax_agent import run_tax_agent
from agents.couple_agent import run_couple_agent
from agents.synthesis_agent import run_synthesis_agent
from reporting import build_plan_report
from storage import list_recent_plans, save_plan


class AIQuotaExceededError(Exception):
  def __init__(self, message: str, retry_after_seconds: int | None = None) -> None:
    super().__init__(message)
    self.retry_after_seconds = retry_after_seconds


class GeminiJSONClient:
  def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
    if not api_key:
      raise ValueError("Missing GEMINI_API_KEY in .env.")

    self.client = genai.Client(api_key=api_key)
    self.model = model

  def generate_json(self, prompt: str) -> dict[str, Any]:
    try:
      response = self.client.models.generate_content(
        model=self.model,
        contents=prompt,
        config=types.GenerateContentConfig(
          response_mime_type="application/json",
          temperature=0.6,
        ),
      )
    except Exception as exc:
      error_text = str(exc)
      if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text or "quota" in error_text.lower():
        retry_after = None
        match = re.search(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", error_text, re.IGNORECASE)
        if match:
          retry_after = int(float(match.group(1)))

        friendly_message = "AI usage is temporarily busy right now. Please wait about a minute and try again."
        if retry_after:
          friendly_message = f"AI usage is temporarily busy right now. Please try again in about {retry_after} seconds."

        raise AIQuotaExceededError(friendly_message, retry_after_seconds=retry_after) from exc

      raise

    text = (response.text or "").strip()
    if not text:
      raise ValueError("Gemini returned an empty response.")

    return json.loads(text)


class FinanceMentorService:
  def __init__(self) -> None:
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    self.llm = GeminiJSONClient(api_key=api_key, model=model)

  def generate_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
    self._validate_payload(payload)

    health = run_health_agent(payload, self.llm)
    fire = run_fire_agent(payload, self.llm)
    life_event = run_life_event_agent(payload, self.llm)
    tax = run_tax_agent(payload, self.llm)
    couple = run_couple_agent(payload, self.llm)
    portfolio = run_portfolio_agent(payload, self.llm)
    overview = run_synthesis_agent(payload, health, fire, life_event, tax, couple, portfolio, self.llm)
    report_payload = {
      "overview": overview,
      "health": health,
      "fire": fire,
      "life_event": life_event,
      "tax": tax,
      "couple": couple,
      "portfolio": portfolio,
    }
    report_text = build_plan_report(report_payload)

    plan_id = save_plan(
      title=overview["title"],
      summary=overview["summary"],
      monthly_sip=fire["monthly_sip"],
      money_health_score=health["score"],
      payload_json=json.dumps(payload),
      report_text=report_text,
      response_json=json.dumps(report_payload),
    )

    return {
      "plan_id": plan_id,
      "report_available": True,
      "overview": overview,
      "health": health,
      "fire": fire,
      "life_event": life_event,
      "tax": tax,
      "couple": couple,
      "portfolio": portfolio,
      "saved_plans": list_recent_plans(),
    }

  @staticmethod
  def _validate_payload(payload: dict[str, Any]) -> None:
    required_fields = [
      "age",
      "monthly_income",
      "monthly_expenses",
      "emergency_fund",
      "insurance_cover",
      "debt_outstanding",
      "tax_savings",
      "existing_investments",
      "retirement_corpus",
      "fire_age",
      "goal_corpus",
      "expected_return",
      "equity_allocation",
      "alt_allocation",
      "expense_ratio",
      "portfolio_xirr",
      "benchmark_return",
      "life_event",
      "event_amount",
      "risk_profile",
      "tax_bracket",
      "annual_salary",
      "other_deductions",
      "declared_deductions",
      "preferred_regime",
      "your_monthly_income",
      "partner_monthly_income",
      "household_expenses",
      "combined_investments",
      "combined_insurance",
      "housing_status",
      "fund_count",
      "primary_goal",
    ]

    missing = [field for field in required_fields if field not in payload]
    if missing:
      raise ValueError(f"Missing required fields: {', '.join(missing)}")
