from __future__ import annotations

from flask import redirect, render_template, request, session, url_for

from db import get_user_by_email, verify_password

from .auth import get_username, login_required
from .data_helpers import load_csv_data, normalize_purchase, normalize_sales


def register_page_routes(app):
    data_dir = app.config.get("DATA_DIR")

    def _get_purchase_customers() -> list[str]:
        df = load_csv_data("purchase.csv", data_dir)
        if df is None:
            df = load_csv_data("final purchase.csv", data_dir)
        df = normalize_purchase(df) if df is not None else None
        if df is None or len(df) == 0 or "vendor" not in df.columns:
            return []
        vendors = (
            df["vendor"]
            .astype(str)
            .map(lambda v: v.strip())
            .loc[lambda s: s.ne("")]
            .dropna()
            .unique()
            .tolist()
        )
        return sorted(vendors, key=lambda v: v.lower())

    def _get_sales_cities() -> list[str]:
        df = load_csv_data("sales.csv", data_dir)
        if df is None:
            df = load_csv_data("final sale.csv", data_dir)
        df = normalize_sales(df) if df is not None else None
        if df is None or len(df) == 0 or "city" not in df.columns:
            return []
        cities = (
            df["city"]
            .astype(str)
            .map(lambda v: v.strip())
            .loc[lambda s: s.ne("")]
            .dropna()
            .unique()
            .tolist()
        )
        return sorted(cities, key=lambda v: v.lower())

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

    @app.route("/purchase-filter", methods=["POST"])
    @login_required
    def set_purchase_filter():
        """Set purchase customer/vendor + date filters in session."""

        customer = (request.form.get("customer") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()

        session["purchase_customer_filter"] = customer
        session["start_date_filter"] = start_date
        session["end_date_filter"] = end_date

        gf = session.get("global_filters") or {}
        gf.update({"purchase_customer": customer, "start_date": start_date, "end_date": end_date})
        session["global_filters"] = gf

        return redirect(request.form.get("next") or url_for("purchase"))

    @app.route("/purchase-filter/clear", methods=["POST"])
    @login_required
    def clear_purchase_filter():
        """Clear purchase customer/vendor + date filters."""

        session.pop("purchase_customer_filter", None)
        session.pop("start_date_filter", None)
        session.pop("end_date_filter", None)

        gf = session.get("global_filters") or {}
        gf.pop("purchase_customer", None)
        gf.pop("start_date", None)
        gf.pop("end_date", None)
        session["global_filters"] = gf if gf else None
        if session.get("global_filters") is None:
            session.pop("global_filters", None)

        return redirect(request.form.get("next") or url_for("purchase"))

    @app.route("/sales-filter", methods=["POST"])
    @login_required
    def set_sales_filter():
        """Set sales city + date filters in session."""

        city = (request.form.get("city") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()

        session["sales_city_filter"] = city
        session["start_date_filter"] = start_date
        session["end_date_filter"] = end_date

        gf = session.get("global_filters") or {}
        gf.update({"sales_city": city, "start_date": start_date, "end_date": end_date})
        session["global_filters"] = gf

        return redirect(request.form.get("next") or url_for("sales"))

    @app.route("/sales-filter/clear", methods=["POST"])
    @login_required
    def clear_sales_filter():
        """Clear sales city + date filters."""

        session.pop("sales_city_filter", None)
        session.pop("start_date_filter", None)
        session.pop("end_date_filter", None)

        gf = session.get("global_filters") or {}
        gf.pop("sales_city", None)
        gf.pop("start_date", None)
        gf.pop("end_date", None)
        session["global_filters"] = gf if gf else None
        if session.get("global_filters") is None:
            session.pop("global_filters", None)

        return redirect(request.form.get("next") or url_for("sales"))

    @app.route("/comparison-filter", methods=["POST"])
    @login_required
    def set_comparison_filter():
        """Set comparison city + date filters in session."""

        city = (request.form.get("city") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()

        session["comparison_city_filter"] = city
        session["start_date_filter"] = start_date
        session["end_date_filter"] = end_date

        gf = session.get("global_filters") or {}
        gf.update({"comparison_city": city, "start_date": start_date, "end_date": end_date})
        session["global_filters"] = gf

        return redirect(request.form.get("next") or url_for("comparison"))

    @app.route("/comparison-filter/clear", methods=["POST"])
    @login_required
    def clear_comparison_filter():
        """Clear comparison city + date filters."""

        session.pop("comparison_city_filter", None)
        session.pop("start_date_filter", None)
        session.pop("end_date_filter", None)

        gf = session.get("global_filters") or {}
        gf.pop("comparison_city", None)
        gf.pop("start_date", None)
        gf.pop("end_date", None)
        session["global_filters"] = gf if gf else None
        if session.get("global_filters") is None:
            session.pop("global_filters", None)

        return redirect(request.form.get("next") or url_for("comparison"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """Main dashboard page."""

        return render_template("dashboard.html", username=get_username())

    @app.route("/sales")
    @login_required
    def sales():
        """Sales Dashboard."""

        return render_template(
            "sales.html",
            username=get_username(),
            sales_cities=_get_sales_cities(),
        )

    @app.route("/purchase")
    @login_required
    def purchase():
        """Purchase Dashboard."""

        return render_template(
            "purchase.html",
            username=get_username(),
            purchase_customers=_get_purchase_customers(),
        )

    @app.route("/comparison")
    @login_required
    def comparison():
        """Sales vs Purchase Comparison."""

        return render_template(
            "comparison.html",
            username=get_username(),
            sales_cities=_get_sales_cities(),
        )

    @app.route("/prediction")
    @login_required
    def prediction():
        """Predictive analysis page."""

        return render_template("prediction.html", username=get_username())
