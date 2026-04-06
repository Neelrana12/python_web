from __future__ import annotations

from flask import redirect, render_template, request, session, url_for

from db import get_user_by_email, verify_password

from .auth import get_username, login_required


def register_page_routes(app):
    @app.route("/")
    def home():
        """Home page - redirect based on login status."""

        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page."""

        if request.method == "POST":
            email = (request.form.get("username") or "").strip().lower()
            password = request.form.get("password") or ""

            user = get_user_by_email(email)
            if user and verify_password(password, user["password"]):
                session["user_id"] = user["id"]
                session["email"] = user["email"]
                session["role"] = user["role"]
                session["username"] = user["email"]
                session.permanent = True
                return redirect(url_for("dashboard"))

            error = "Invalid email or password"
            return render_template("login.html", error=error)

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        """Logout - clear session."""

        session.clear()
        return redirect(url_for("login"))

    @app.route("/global-filter", methods=["POST"])
    @login_required
    def set_global_filter():
        """Set global region/date filters in session."""

        region = (request.form.get("region") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()
        session["region_filter"] = region
        session["start_date_filter"] = start_date
        session["end_date_filter"] = end_date
        session["global_filters"] = {"region": region, "start_date": start_date, "end_date": end_date}
        return redirect(request.form.get("next") or url_for("dashboard"))

    @app.route("/global-filter/clear", methods=["POST"])
    @login_required
    def clear_global_filter():
        """Clear session filters."""

        session.pop("region_filter", None)
        session.pop("start_date_filter", None)
        session.pop("end_date_filter", None)
        session.pop("global_filters", None)
        return redirect(request.form.get("next") or url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """Main dashboard page."""

        return render_template("dashboard.html", username=get_username())

    @app.route("/sales")
    @login_required
    def sales():
        """Sales Dashboard."""

        return render_template("sales.html", username=get_username())

    @app.route("/purchase")
    @login_required
    def purchase():
        """Purchase Dashboard."""

        return render_template("purchase.html", username=get_username())

    @app.route("/comparison")
    @login_required
    def comparison():
        """Sales vs Purchase Comparison."""

        return render_template("comparison.html", username=get_username())

    @app.route("/prediction")
    @login_required
    def prediction():
        """Predictive analysis page."""

        return render_template("prediction.html", username=get_username())
