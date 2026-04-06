import os
import sqlite3
from typing import Any, Dict, Optional

import bcrypt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'manager'))
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE
            );
            """
        )
        conn.commit()


def add_report(filename: str, db_path: str = DB_PATH) -> int:
    safe_name = (filename or "").strip()
    if not safe_name:
        raise ValueError("filename required")

    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT OR IGNORE INTO reports (filename) VALUES (?)",
            (safe_name,),
        )
        conn.commit()
        return int(cursor.lastrowid or 0)


def list_reports(db_path: str = DB_PATH) -> list[str]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT filename FROM reports ORDER BY LOWER(filename)").fetchall()
    return [str(r["filename"]) for r in rows]


def delete_report_by_filename(filename: str, db_path: str = DB_PATH) -> int:
    safe_name = (filename or "").strip()
    if not safe_name:
        return 0

    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM reports WHERE filename = ?", (safe_name,))
        conn.commit()
        return int(cursor.rowcount)


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_user_by_email(email: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, email, password, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if not row:
        return None
    return dict(row)


def create_user(email: str, plain_password: str, role: str = "manager", db_path: str = DB_PATH) -> int:
    if role not in {"admin", "manager"}:
        raise ValueError("role must be 'admin' or 'manager'")

    email_normalized = email.strip().lower()
    password_hashed = hash_password(plain_password)

    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
            (email_normalized, password_hashed, role),
        )
        conn.commit()
        return int(cursor.lastrowid)


def ensure_default_admin(db_path: str = DB_PATH) -> None:
    """Create default demo users (admin + manager) if not already present."""
    default_password = "1234"

    admin_email = "admin@gmail.com"
    if not get_user_by_email(admin_email, db_path=db_path):
        create_user(admin_email, default_password, role="admin", db_path=db_path)

    manager_email = "manager@gmail.com"
    if not get_user_by_email(manager_email, db_path=db_path):
        create_user(manager_email, default_password, role="manager", db_path=db_path)


if __name__ == "__main__":
    # Minimal CLI usage (optional):
    #   python db.py
    # Creates app.db + users table + default demo users.
    init_db()
    ensure_default_admin()
    print("Database initialized.")
    print("Default admin: admin@gmail.com / 1234")
    print("Default manager: manager@gmail.com / 1234")
