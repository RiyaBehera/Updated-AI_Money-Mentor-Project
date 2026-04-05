import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "finance_mentor.db"


def init_db() -> None:
  with sqlite3.connect(DB_PATH) as connection:
    connection.execute(
      """
      CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        monthly_sip REAL NOT NULL,
        money_health_score INTEGER NOT NULL,
        payload_json TEXT NOT NULL,
        report_text TEXT NOT NULL DEFAULT '',
        response_json TEXT NOT NULL DEFAULT ''
      )
      """
    )
    columns = {row[1] for row in connection.execute("PRAGMA table_info(plans)").fetchall()}
    if "report_text" not in columns:
      connection.execute("ALTER TABLE plans ADD COLUMN report_text TEXT NOT NULL DEFAULT ''")
    if "response_json" not in columns:
      connection.execute("ALTER TABLE plans ADD COLUMN response_json TEXT NOT NULL DEFAULT ''")
    connection.commit()


def save_plan(
  title: str,
  summary: str,
  monthly_sip: float,
  money_health_score: int,
  payload_json: str,
  report_text: str,
  response_json: str,
) -> int:
  with sqlite3.connect(DB_PATH) as connection:
    cursor = connection.execute(
      """
      INSERT INTO plans (title, summary, monthly_sip, money_health_score, payload_json, report_text, response_json)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      """,
      (title, summary, monthly_sip, money_health_score, payload_json, report_text, response_json),
    )
    connection.commit()
    return int(cursor.lastrowid)


def list_recent_plans(limit: int = 8) -> list[dict]:
  with sqlite3.connect(DB_PATH) as connection:
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
      """
      SELECT id, created_at, title, summary, monthly_sip, money_health_score
      FROM plans
      ORDER BY id DESC
      LIMIT ?
      """,
      (limit,),
    ).fetchall()

  return [dict(row) for row in rows]


def get_plan_report(plan_id: int) -> dict | None:
  with sqlite3.connect(DB_PATH) as connection:
    connection.row_factory = sqlite3.Row
    row = connection.execute(
      """
      SELECT id, title, report_text, response_json
      FROM plans
      WHERE id = ?
      """,
      (plan_id,),
    ).fetchone()

  return dict(row) if row else None
