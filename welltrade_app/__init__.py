"""Welltrade Surgipharma analytics Flask app package.

This package exists to keep the main entrypoint (app.py) small and readable.
"""

from .app_factory import create_app

__all__ = ["create_app"]
