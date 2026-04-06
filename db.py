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
        conn.commit()


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
    """Create default admin user if not already present."""
    default_email = "admin@gmail.com"
    default_password = "1234"

    existing = get_user_by_email(default_email, db_path=db_path)
    if existing:
        return

    create_user(default_email, default_password, role="admin", db_path=db_path)


if __name__ == "__main__":
    # Minimal CLI usage (optional):
    #   python db.py
    # Creates app.db + users table + default admin.
    init_db()
    ensure_default_admin()
    print("Database initialized.")
    print("Default admin: admin@gmail.com / 1234")
