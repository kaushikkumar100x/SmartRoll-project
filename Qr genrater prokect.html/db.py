"""SQLite database helpers.

Uses parameterized queries throughout to prevent SQL injection.
"""
import sqlite3
from contextlib import contextmanager
from typing import Iterator


_DB_PATH: str = ""


def init_db(db_path: str) -> None:
    """Initialize DB schema if it does not exist."""
    global _DB_PATH
    _DB_PATH = db_path
    with get_conn() as conn:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('teacher', 'student')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                class_name TEXT NOT NULL,
                token TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (student_email, token)
            );

            CREATE TABLE IF NOT EXISTS qr_sessions (
                token TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                class_name TEXT NOT NULL,
                teacher_email TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                teacher_email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_name TEXT,
                uploader_email TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_attendance_subject ON attendance(subject);
            CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_email);
            """
        )
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Context-managed SQLite connection that returns rows as dicts."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute a write query. Returns lastrowid."""
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid or 0
