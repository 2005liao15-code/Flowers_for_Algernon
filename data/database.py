import sqlite3
import os
from typing import Optional, Any

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "algernon.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS maze_trials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                trial_id INTEGER NOT NULL,
                completion_time REAL NOT NULL,
                path_corrections INTEGER NOT NULL DEFAULT 0,
                hesitation_count INTEGER NOT NULL DEFAULT 0,
                bullet_time_used INTEGER NOT NULL DEFAULT 0,
                bullet_time_duration REAL NOT NULL DEFAULT 0.0,
                wrong_path_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES game_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                answer_index INTEGER NOT NULL,
                response_time REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES game_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS reading_dwell (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                stage_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                duration REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES game_sessions(id)
            );
        """)
        conn.commit()


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def create_session() -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO game_sessions (created_at) VALUES (datetime('now'))"
        )
        return cur.lastrowid


def end_session(session_id: int):
    with _connect() as conn:
        conn.execute(
            "UPDATE game_sessions SET completed_at = datetime('now') WHERE id = ?",
            (session_id,),
        )


def get_session(session_id: int) -> Optional[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM game_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return dict(row) if row else None


def list_sessions() -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM game_sessions ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_session(session_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM reading_dwell WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM quiz_answers WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM maze_trials WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM game_sessions WHERE id = ?", (session_id,))


# ---------------------------------------------------------------------------
# Maze trials
# ---------------------------------------------------------------------------

def insert_maze_trial(
    session_id: int,
    trial_id: int,
    completion_time: float,
    path_corrections: int = 0,
    hesitation_count: int = 0,
    bullet_time_used: int = 0,
    bullet_time_duration: float = 0.0,
    wrong_path_count: int = 0,
) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO maze_trials
               (session_id, trial_id, completion_time, path_corrections,
                hesitation_count, bullet_time_used, bullet_time_duration,
                wrong_path_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, trial_id, completion_time, path_corrections,
             hesitation_count, bullet_time_used, bullet_time_duration,
             wrong_path_count),
        )
        return cur.lastrowid


def get_maze_trials(session_id: int) -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM maze_trials WHERE session_id = ? ORDER BY trial_id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_maze_trial(row_id: int) -> Optional[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM maze_trials WHERE id = ?", (row_id,)
        ).fetchone()
        return dict(row) if row else None


def update_maze_trial(row_id: int, **kwargs):
    allowed = {
        "completion_time", "path_corrections", "hesitation_count",
        "bullet_time_used", "bullet_time_duration", "wrong_path_count",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [row_id]
    with _connect() as conn:
        conn.execute(
            f"UPDATE maze_trials SET {set_clause} WHERE id = ?", values
        )


def delete_maze_trial(row_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM maze_trials WHERE id = ?", (row_id,))


def delete_maze_trials_by_session(session_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM maze_trials WHERE session_id = ?", (session_id,))


# ---------------------------------------------------------------------------
# Quiz answers
# ---------------------------------------------------------------------------

def insert_quiz_answer(
    session_id: int,
    question_id: str,
    answer_index: int,
    response_time: float,
) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO quiz_answers
               (session_id, question_id, answer_index, response_time)
               VALUES (?, ?, ?, ?)""",
            (session_id, question_id, answer_index, response_time),
        )
        return cur.lastrowid


def get_quiz_answers(session_id: int) -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM quiz_answers WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_quiz_answer(row_id: int) -> Optional[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM quiz_answers WHERE id = ?", (row_id,)
        ).fetchone()
        return dict(row) if row else None


def update_quiz_answer(row_id: int, **kwargs):
    allowed = {"answer_index", "response_time"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [row_id]
    with _connect() as conn:
        conn.execute(
            f"UPDATE quiz_answers SET {set_clause} WHERE id = ?", values
        )


def delete_quiz_answer(row_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM quiz_answers WHERE id = ?", (row_id,))


def delete_quiz_answers_by_session(session_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM quiz_answers WHERE session_id = ?", (session_id,))


# ---------------------------------------------------------------------------
# Reading dwell
# ---------------------------------------------------------------------------

def insert_reading_dwell(
    session_id: int,
    stage_id: str,
    section_id: str,
    duration: float,
) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO reading_dwell
               (session_id, stage_id, section_id, duration)
               VALUES (?, ?, ?, ?)""",
            (session_id, stage_id, section_id, duration),
        )
        return cur.lastrowid


def get_reading_dwells(session_id: int) -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM reading_dwell WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_reading_dwell(row_id: int) -> Optional[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM reading_dwell WHERE id = ?", (row_id,)
        ).fetchone()
        return dict(row) if row else None


def update_reading_dwell(row_id: int, **kwargs):
    allowed = {"duration"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [row_id]
    with _connect() as conn:
        conn.execute(
            f"UPDATE reading_dwell SET {set_clause} WHERE id = ?", values
        )


def delete_reading_dwell(row_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM reading_dwell WHERE id = ?", (row_id,))


def delete_reading_dwells_by_session(session_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM reading_dwell WHERE session_id = ?", (session_id,))


# ---------------------------------------------------------------------------
# ML convenience
# ---------------------------------------------------------------------------

def get_session_maze_vector(session_id: int) -> Optional[dict[str, Any]]:
    trials = get_maze_trials(session_id)
    if not trials:
        return None
    count = len(trials)
    return {
        "session_id": session_id,
        "trial_count": count,
        "avg_completion_time": sum(t["completion_time"] for t in trials) / count,
        "avg_path_corrections": sum(t["path_corrections"] for t in trials) / count,
        "avg_hesitation_count": sum(t["hesitation_count"] for t in trials) / count,
        "total_bullet_time_used": sum(t["bullet_time_used"] for t in trials),
        "total_bullet_time_duration": sum(t["bullet_time_duration"] for t in trials),
        "total_wrong_paths": sum(t["wrong_path_count"] for t in trials),
    }


def get_session_quiz_vector(session_id: int) -> Optional[dict[str, Any]]:
    answers = get_quiz_answers(session_id)
    if not answers:
        return None
    count = len(answers)
    return {
        "session_id": session_id,
        "quiz_count": count,
        "avg_response_time": sum(a["response_time"] for a in answers) / count,
    }


def get_session_dwell_vector(session_id: int) -> Optional[dict[str, Any]]:
    dwells = get_reading_dwells(session_id)
    if not dwells:
        return None
    total = sum(d["duration"] for d in dwells)
    return {
        "session_id": session_id,
        "section_count": len(dwells),
        "total_duration": total,
        "avg_duration": total / len(dwells),
    }


_init_done = False


def _ensure_init():
    global _init_done
    if not _init_done:
        os.makedirs(DB_DIR, exist_ok=True)
        init_db()
        _init_done = True


_ensure_init()
