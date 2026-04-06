from __future__ import annotations

import os

import pandas as pd
from flask import abort, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .auth import admin_required, get_username, login_required
from .file_validation import validate_csv, validate_pdf


def register_file_routes(app):
    data_dir = app.config["DATA_DIR"]
    reports_dir = app.config["REPORTS_DIR"]
    allowed_report_extensions = app.config["ALLOWED_REPORT_EXTENSIONS"]

    @app.route("/upload", methods=["POST"])
    @admin_required
    def upload():
        """Admin-only: upload CSV (sales/purchase) and PDF reports."""

        upload_kind = (request.form.get("upload_kind") or "").strip().lower()
        uploaded_file = request.files.get("file")

        if upload_kind not in {"sales_csv", "purchase_csv", "report_pdf"}:
            return "Invalid upload_kind", 400
        if not uploaded_file or not uploaded_file.filename:
            return "No file uploaded", 400

        original_name = uploaded_file.filename
        ext = os.path.splitext(original_name)[1].lower()

        if upload_kind in {"sales_csv", "purchase_csv"}:
            if ext != ".csv":
                return "Only .csv files allowed", 400
            if not validate_csv(uploaded_file):
                return "Invalid CSV file", 400

            try:
                df = pd.read_csv(uploaded_file, header=None)
                uploaded_file.stream.seek(0)
            except Exception:
                return "Invalid CSV file", 400

            col_count = df.shape[1]
            if upload_kind == "sales_csv" and col_count != 4:
                return "Sales CSV must have 4 columns: date, customer, city, amount", 400
            if upload_kind == "purchase_csv" and col_count not in (3, 4):
                return "Purchase CSV must have 3-4 columns", 400

            target_name = "sales.csv" if upload_kind == "sales_csv" else "purchase.csv"
            target_path = os.path.join(data_dir, secure_filename(target_name))
            uploaded_file.save(target_path)
            return redirect(url_for("sales" if upload_kind == "sales_csv" else "purchase"))

        if ext not in allowed_report_extensions:
            return "Only PDF reports allowed", 400
        if not validate_pdf(uploaded_file):
            return "Invalid PDF file", 400

        safe_name = secure_filename(original_name)
        if not safe_name.lower().endswith(".pdf"):
            safe_name = safe_name + ".pdf"

        target_path = os.path.join(reports_dir, safe_name)
        if os.path.exists(target_path):
            base, _ = os.path.splitext(safe_name)
            counter = 1
            while os.path.exists(os.path.join(reports_dir, f"{base}-{counter}.pdf")):
                counter += 1
            target_path = os.path.join(reports_dir, f"{base}-{counter}.pdf")

        uploaded_file.save(target_path)
        return redirect(url_for("reports"))

    @app.route("/reports")
    @login_required
    def reports():
        """Report library: list PDF reports (admin + manager)."""

        files = []
        try:
            for name in os.listdir(reports_dir):
                if name.lower().endswith(".pdf"):
                    files.append(name)
        except FileNotFoundError:
            files = []

        files.sort(key=lambda x: x.lower())
        return render_template("reports.html", username=get_username(), files=files)

    @app.route("/download/<path:filename>")
    @login_required
    def download(filename: str):
        """Simple file download (PBIX dashboards + PDF reports)."""

        safe_name = secure_filename(filename)

        if safe_name.lower().endswith(".pbix"):
            return send_from_directory(
                os.path.join(app.static_folder, "reports"),
                safe_name,
                as_attachment=True,
            )

        if safe_name.lower().endswith(".pdf"):
            return send_from_directory(reports_dir, safe_name, as_attachment=True)

        abort(404)

    @app.route("/reports/delete/<path:filename>", methods=["POST"])
    @admin_required
    def delete_report(filename: str):
        """Admin-only: delete a PDF report from the report library."""

        safe_name = secure_filename(filename)
        if not safe_name.lower().endswith(".pdf"):
            abort(404)

        full_path = os.path.join(reports_dir, safe_name)
        if not os.path.exists(full_path):
            abort(404)

        try:
            os.remove(full_path)
        except Exception:
            return "Failed to delete report", 500

        return redirect(url_for("reports"))
