
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Store the database inside the project.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "researchx.db"


def get_connection():
    """Create a database connection."""

    connection = sqlite3.connect(DATABASE_PATH, timeout=30)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the research history table if needed."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                report TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_research(topic: str, report: str) -> int:
    """Save a completed research report and return its ID."""

    if not topic or not topic.strip():
        raise ValueError("Research topic cannot be empty.")

    if not report or not report.strip():
        raise ValueError("Research report cannot be empty.")

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO research_history (
                topic,
                report,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (topic.strip(), report, created_at),
        )

        return cursor.lastrowid


def get_research_history(limit: int = 50) -> list[dict]:
    """Return the most recent research tasks."""

    if not 1 <= limit <= 500:
        raise ValueError("Limit must be between 1 and 500.")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, topic, created_at
            FROM research_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_research_by_id(research_id: int) -> dict | None:
    """Retrieve a saved research report by its ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, topic, report, created_at
            FROM research_history
            WHERE id = ?
            """,
            (research_id,),
        ).fetchone()

    return dict(row) if row else None


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DATABASE_PATH}")

