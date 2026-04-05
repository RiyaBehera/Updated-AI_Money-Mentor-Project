from pathlib import Path
import io

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from pypdf import PdfReader

from service import AIQuotaExceededError, FinanceMentorService
from storage import get_plan_report, init_db, list_recent_plans


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

load_dotenv(ROOT_DIR / ".env")
init_db()

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

service = FinanceMentorService()


def _to_number(value, default=0.0):
  try:
    return float(value)
  except (TypeError, ValueError):
    return float(default)


def _read_pdf_text(file_storage):
  if not file_storage or not getattr(file_storage, "filename", ""):
    return ""

  try:
    reader = PdfReader(file_storage.stream)
    pages = []
    for page in reader.pages[:5]:
      pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()
  except Exception:
    return ""


def _validate_pdf_upload(file_storage, field_name):
  if not file_storage or not getattr(file_storage, "filename", ""):
    return None

  filename = file_storage.filename.lower()
  if not filename.endswith(".pdf"):
    raise ValueError(f"{field_name} must be a PDF file.")

  file_storage.stream.seek(0, 2)
  size = file_storage.stream.tell()
  file_storage.stream.seek(0)

  if size > 5 * 1024 * 1024:
    raise ValueError(f"{field_name} must be smaller than 5 MB.")

  return file_storage


def _build_payload():
  if request.content_type and "multipart/form-data" in request.content_type:
    form = request.form
    files = request.files
    form16_file = _validate_pdf_upload(files.get("form16File"), "Form 16")
    portfolio_file = _validate_pdf_upload(files.get("portfolioStatement"), "Portfolio statement")

    return {
      "age": _to_number(form.get("age")),
      "monthly_income": _to_number(form.get("monthlyIncome")),
      "monthly_expenses": _to_number(form.get("monthlyExpenses")),
      "salary_growth": _to_number(form.get("salaryGrowth")),
      "existing_investments": _to_number(form.get("existingInvestments")),
      "fire_age": _to_number(form.get("fireAge")),
      "goal_corpus": _to_number(form.get("goalCorpus")),
      "expected_return": _to_number(form.get("expectedReturn")),
      "primary_goal": form.get("primaryGoal", ""),
      "emergency_fund": _to_number(form.get("emergencyFund")),
      "insurance_cover": _to_number(form.get("insuranceCover")),
      "debt_outstanding": _to_number(form.get("debtOutstanding")),
      "tax_savings": _to_number(form.get("taxSavings")),
      "retirement_corpus": _to_number(form.get("retirementCorpus")),
      "equity_allocation": _to_number(form.get("equityAllocation")),
      "alt_allocation": _to_number(form.get("altAllocation")),
      "life_event": form.get("lifeEvent", ""),
      "event_amount": _to_number(form.get("eventAmount")),
      "risk_profile": form.get("riskProfile", ""),
      "tax_bracket": _to_number(form.get("taxBracket")),
      "annual_salary": _to_number(form.get("annualSalary")),
      "other_deductions": _to_number(form.get("otherDeductions")),
      "declared_deductions": _to_number(form.get("declaredDeductions")),
      "preferred_regime": form.get("preferredRegime", "compare"),
      "form16_filename": form16_file.filename if form16_file else "",
      "form16_text": _read_pdf_text(form16_file),
      "your_monthly_income": _to_number(form.get("yourMonthlyIncome")),
      "partner_monthly_income": _to_number(form.get("partnerMonthlyIncome")),
      "household_expenses": _to_number(form.get("householdExpenses")),
      "combined_investments": _to_number(form.get("combinedInvestments")),
      "combined_insurance": _to_number(form.get("combinedInsurance")),
      "housing_status": form.get("housingStatus", ""),
      "portfolio_xirr": _to_number(form.get("portfolioXirr")),
      "benchmark_return": _to_number(form.get("benchmarkReturn")),
      "expense_ratio": _to_number(form.get("expenseRatio")),
      "fund_count": _to_number(form.get("fundCount")),
      "portfolio_statement_filename": portfolio_file.filename if portfolio_file else "",
      "portfolio_statement_text": _read_pdf_text(portfolio_file),
    }

  return request.get_json(silent=True) or {}


@app.get("/")
def index():
  return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/health")
def health_check():
  return jsonify({"status": "ok"})


@app.get("/api/plans")
def get_saved_plans():
  return jsonify({"plans": list_recent_plans()})


@app.get("/api/plans/<int:plan_id>/report")
def download_plan_report(plan_id: int):
  plan = get_plan_report(plan_id)
  if not plan:
    return jsonify({"error": "Plan report not found."}), 404

  report_bytes = io.BytesIO((plan.get("report_text", "") or "").encode("utf-8"))
  safe_name = "".join(char if char.isalnum() else "_" for char in plan["title"]).strip("_") or "finance_plan"
  return send_file(
    report_bytes,
    as_attachment=True,
    download_name=f"{safe_name}_{plan_id}.txt",
    mimetype="text/plain; charset=utf-8",
  )


@app.post("/api/generate-plan")
def generate_plan():
  try:
    payload = _build_payload()
    response = service.generate_plan(payload)
    return jsonify(response)
  except AIQuotaExceededError as exc:
    response = jsonify({"error": str(exc)})
    if exc.retry_after_seconds:
      response.headers["Retry-After"] = str(exc.retry_after_seconds)
    return response, 429
  except ValueError as exc:
    return jsonify({"error": str(exc)}), 400
  except Exception as exc:
    return jsonify({"error": f"Server error: {exc}"}), 500


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)
