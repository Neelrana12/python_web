from __future__ import annotations

import os
from datetime import timedelta

from flask import Flask

from db import ensure_default_admin, init_db

from .routes_api import register_api_routes
from .routes_files import register_file_routes
from .routes_pages import register_page_routes


def create_app(*, base_dir: str) -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    app.secret_key = "welltrade-secret-2024"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

    storage_dir = os.environ.get("WELLTRADE_STORAGE_DIR") or base_dir
    data_dir = os.path.join(storage_dir, "data")
    reports_dir = os.path.join(storage_dir, "reports")
    uploads_dir = os.path.join(storage_dir, "uploads")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)

    max_upload_mb = 10
    app.config.update(
        BASE_DIR=base_dir,
        DATA_DIR=data_dir,
        REPORTS_DIR=reports_dir,
        UPLOADS_DIR=uploads_dir,
        MAX_UPLOAD_MB=max_upload_mb,
        MAX_CONTENT_LENGTH=max_upload_mb * 1024 * 1024,
        ALLOWED_REPORT_EXTENSIONS={".pdf"},
    )

    init_db()
    ensure_default_admin()

    @app.errorhandler(413)
    def file_too_large(_e):
        return f"File too large. Max {max_upload_mb}MB.", 413

    register_page_routes(app)
    register_api_routes(app)
    register_file_routes(app)

    return app
