from __future__ import annotations

from functools import wraps

from flask import redirect, session, url_for


def login_required(func):
    """User must be logged in."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    """User must be admin."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            return "Forbidden", 403
        return func(*args, **kwargs)

    return wrapper


def get_username() -> str | None:
    """Get current username for templates."""

    return session.get("username") or session.get("email")
