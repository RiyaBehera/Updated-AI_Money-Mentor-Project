# AI Money Mentor

AI Money Mentor is a full-stack personal finance planning application built to make high-quality financial guidance accessible to everyday users. The platform takes structured financial inputs, runs them through multiple specialist AI agents, and produces a combined financial blueprint covering planning, scoring, tax, life events, couples, and portfolio analysis.

## What The Project Does

The app helps a user:

- plan for financial independence and retirement
- understand their overall financial health
- make better money decisions during major life events
- compare tax regimes and identify tax-saving opportunities
- create a joint plan for couples
- analyse a mutual fund portfolio for overlap, cost, and rebalancing

## Core Modules

1. `FIRE Path Planner`
2. `Money Health Score`
3. `Life Event Financial Advisor`
4. `Tax Wizard`
5. `Couple's Money Planner`
6. `Mutual Fund Portfolio X-Ray`

## Tech Stack

Frontend:

- `HTML` for layout
- `CSS` for styling and responsive design
- `Vanilla JavaScript` for form handling, navigation, API calls, and chart rendering

Backend:

- `Python`
- `Flask` for API routes and frontend serving
- `google-genai` for Gemini integration
- `pypdf` for optional PDF parsing
- `SQLite` for saved-plan persistence

## Project Structure

- `.env`
- `requirements.txt`
- `finance_mentor.db`
- `frontend/index.html`
- `frontend/styles.css`
- `frontend/script.js`
- `backend/main.py`
- `backend/service.py`
- `backend/storage.py`
- `backend/agents/`

## How It Works

1. The user fills the planner in the frontend.
2. The frontend sends the data, including optional PDFs, to `POST /api/generate-plan`.
3. `backend/main.py` parses the request and validates uploads.
4. `backend/service.py` sends the payload to specialist finance agents.
5. Each agent generates a focused output for one module.
6. The synthesis agent combines all module outputs into one final plan.
7. The backend saves the plan in SQLite.
8. The frontend renders the plan section by section.

## Frontend Features

- guided multi-step input wizard
- separate section-by-section output navigation with previous and next controls
- sticky side sliders for input and output
- active section highlighting
- upload validation for PDF files
- simple charts for growth, allocation, and health score
- saved plan history display
- downloadable text report for each generated plan

## Backend Features

- Gemini-powered multi-agent orchestration
- clean separation between routing and business logic
- optional PDF text extraction
- slab-based India tax comparison
- SQLite persistence for generated plans
- downloadable saved plan report endpoint
- user-friendly rate-limit handling for Gemini quota exhaustion

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add your Gemini key to `.env`.

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

3. Run the backend:

```bash
python backend/main.py
```

4. Open:

```text
http://localhost:5000
```

## Important Notes

- If the frontend is opened outside Flask, it falls back to `http://127.0.0.1:5000`.
- Uploaded files must be PDFs and must stay under 5 MB.
- Saved plans are stored in `finance_mentor.db`.
- Generated plans can be downloaded as text reports from the final `Saved Plans` section in Planner Output.
- If Gemini quota is exhausted, the app now shows a clean retry message instead of the raw API error.
