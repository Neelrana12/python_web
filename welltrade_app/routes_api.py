from __future__ import annotations

from datetime import timedelta

from flask import jsonify, request

from .auth import login_required
from .data_helpers import (
    apply_date_range,
    growth_pct,
    load_csv_data,
    normalize_purchase,
    normalize_sales,
    parse_date,
    previous_period,
)


def get_filter_param(param_name: str, default: str = "") -> str:
    """Get filter from URL param or session (mirrors old behavior)."""

    from flask import request, session

    value = request.args.get(param_name, "").strip()
    if value:
        return value
    gf = session.get("global_filters") or {}
    if param_name == "region":
        return session.get("region_filter") or gf.get("region", "")
    if param_name == "start_date":
        return session.get("start_date_filter") or gf.get("start_date", "")
    if param_name == "end_date":
        return session.get("end_date_filter") or gf.get("end_date", "")
    return default


def register_api_routes(app):
    data_dir = app.config["DATA_DIR"]

    @app.route("/api/sales-data")
    @login_required
    def get_sales_data():
        """API for sales by city."""

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))
        top_n = int(request.args.get("top_n", 10))

        df = load_csv_data("sales.csv", data_dir)
        if df is None:
            df = load_csv_data("final sale.csv", data_dir)
        if df is None:
            return (
                jsonify(
                    {
                        "error": "Sales data not found",
                        "labels": [],
                        "values": [],
                        "total": 0,
                        "top_region": "N/A",
                        "top_n": top_n,
                        "growth_pct": None,
                    }
                ),
                404,
            )

        df = normalize_sales(df)
        if df is None:
            return (
                jsonify(
                    {
                        "error": "Invalid format",
                        "labels": [],
                        "values": [],
                        "total": 0,
                        "top_region": "N/A",
                        "top_n": top_n,
                        "growth_pct": None,
                    }
                ),
                400,
            )

        if region:
            df = df[df["city"].astype(str).str.lower() == region.lower()]

        df_for_growth = df
        df = apply_date_range(df, start_date, end_date)

        if len(df) == 0:
            return jsonify(
                {"labels": [], "values": [], "total": 0, "top_region": "N/A", "growth_pct": None}
            )

        city_totals = df.groupby("city")["amount"].sum().sort_values(ascending=False)
        all_total = city_totals.sum()
        top_cities = city_totals.head(top_n)

        growth = None
        if len(df_for_growth) > 0:
            if start_date and end_date:
                current_total = float(all_total)
                prev_start, prev_end = previous_period(start_date, end_date)
            else:
                auto_end = df_for_growth["date"].max()
                auto_start = auto_end - timedelta(days=29)
                df_current = apply_date_range(df_for_growth, auto_start, auto_end)
                current_total = float(df_current["amount"].sum()) if len(df_current) > 0 else 0.0
                prev_start, prev_end = previous_period(auto_start, auto_end)

            df_prev = apply_date_range(df_for_growth, prev_start, prev_end)
            prev_total = float(df_prev["amount"].sum()) if len(df_prev) > 0 else 0.0
            growth = growth_pct(current_total, prev_total)

        return jsonify(
            {
                "labels": top_cities.index.tolist(),
                "values": [float(v) for v in top_cities.values.tolist()],
                "total": float(all_total),
                "top_region": top_cities.index[0] if len(top_cities) > 0 else "N/A",
                "top_n": top_n,
                "growth_pct": growth,
            }
        )

    @app.route("/api/predict-sales")
    @login_required
    def api_predict_sales():
        """Predict next 3–4 months sales using average monthly growth (no ML)."""

        try:
            months_ahead = int(request.args.get("months", 3))
        except Exception:
            months_ahead = 3
        months_ahead = max(3, min(months_ahead, 4))

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))

        df = load_csv_data("sales.csv", data_dir)
        if df is None:
            df = load_csv_data("final sale.csv", data_dir)
        df = normalize_sales(df) if df is not None else None
        if df is None or len(df) == 0:
            return jsonify({"months": [], "predictions": []})

        if region:
            df = df[df["city"].astype(str).str.lower() == region.lower()]
        df = apply_date_range(df, start_date, end_date)
        if df is None or len(df) == 0:
            return jsonify({"months": [], "predictions": []})

        monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().sort_index()
        last_value = float(monthly.iloc[-1])

        recent = monthly.tail(6)
        pct = recent.pct_change().dropna()
        avg_pct = float(pct.mean()) if len(pct) > 0 else 0.0
        if avg_pct < -0.95:
            avg_pct = -0.95

        last_period = monthly.index[-1]
        months = []
        predictions = []
        for i in range(1, months_ahead + 1):
            next_period = last_period + i
            months.append(next_period.to_timestamp().strftime("%b %Y"))
            predictions.append(max(0.0, last_value * ((1.0 + avg_pct) ** i)))

        return jsonify({"months": months, "predictions": [float(v) for v in predictions]})

    @app.route("/api/predict-purchase")
    @login_required
    def api_predict_purchase():
        """Predict next 3–4 months purchase using average monthly growth (no ML)."""

        try:
            months_ahead = int(request.args.get("months", 3))
        except Exception:
            months_ahead = 3
        months_ahead = max(3, min(months_ahead, 4))

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))

        df = load_csv_data("purchase.csv", data_dir)
        if df is None:
            df = load_csv_data("final purchase.csv", data_dir)
        df = normalize_purchase(df) if df is not None else None
        if df is None or len(df) == 0:
            return jsonify({"months": [], "predictions": []})

        if region:
            if "region" in df.columns:
                df = df[df["region"].astype(str).str.lower() == region.lower()]
            else:
                df = df[df["vendor"].astype(str).str.lower() == region.lower()]

        df = apply_date_range(df, start_date, end_date)
        if df is None or len(df) == 0:
            return jsonify({"months": [], "predictions": []})

        monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum().sort_index()
        last_value = float(monthly.iloc[-1])

        recent = monthly.tail(6)
        pct = recent.pct_change().dropna()
        avg_pct = float(pct.mean()) if len(pct) > 0 else 0.0
        if avg_pct < -0.95:
            avg_pct = -0.95

        last_period = monthly.index[-1]
        months = []
        predictions = []
        for i in range(1, months_ahead + 1):
            next_period = last_period + i
            months.append(next_period.to_timestamp().strftime("%b %Y"))
            predictions.append(max(0.0, last_value * ((1.0 + avg_pct) ** i)))

        return jsonify({"months": months, "predictions": [float(v) for v in predictions]})

    @app.route("/api/purchase-data")
    @login_required
    def get_purchase_data():
        """API for purchase by vendor."""

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))
        top_n = int(request.args.get("top_n", 10))

        df = load_csv_data("purchase.csv", data_dir)
        if df is None:
            df = load_csv_data("final purchase.csv", data_dir)
        if df is None:
            return (
                jsonify(
                    {
                        "error": "Purchase data not found",
                        "labels": [],
                        "values": [],
                        "total": 0,
                        "top_region": "N/A",
                        "top_n": top_n,
                        "growth_pct": None,
                    }
                ),
                404,
            )

        df = normalize_purchase(df)
        if df is None:
            return (
                jsonify(
                    {
                        "error": "Invalid format",
                        "labels": [],
                        "values": [],
                        "total": 0,
                        "top_region": "N/A",
                        "top_n": top_n,
                        "growth_pct": None,
                    }
                ),
                400,
            )

        if region:
            if "region" in df.columns:
                df = df[df["region"].astype(str).str.lower() == region.lower()]
            else:
                df = df[df["vendor"].astype(str).str.lower() == region.lower()]

        df_for_growth = df
        df = apply_date_range(df, start_date, end_date)

        if len(df) == 0:
            return jsonify(
                {"labels": [], "values": [], "total": 0, "top_region": "N/A", "growth_pct": None}
            )

        vendor_totals = df.groupby("vendor")["amount"].sum().sort_values(ascending=False)
        all_total = vendor_totals.sum()
        top_vendors = vendor_totals.head(top_n)

        growth = None
        if len(df_for_growth) > 0:
            if start_date and end_date:
                current_total = float(all_total)
                prev_start, prev_end = previous_period(start_date, end_date)
            else:
                auto_end = df_for_growth["date"].max()
                auto_start = auto_end - timedelta(days=29)
                df_current = apply_date_range(df_for_growth, auto_start, auto_end)
                current_total = float(df_current["amount"].sum()) if len(df_current) > 0 else 0.0
                prev_start, prev_end = previous_period(auto_start, auto_end)

            df_prev = apply_date_range(df_for_growth, prev_start, prev_end)
            prev_total = float(df_prev["amount"].sum()) if len(df_prev) > 0 else 0.0
            growth = growth_pct(current_total, prev_total)

        return jsonify(
            {
                "labels": top_vendors.index.tolist(),
                "values": [float(v) for v in top_vendors.values.tolist()],
                "total": float(all_total),
                "top_region": top_vendors.index[0] if len(top_vendors) > 0 else "N/A",
                "top_n": top_n,
                "growth_pct": growth,
            }
        )

    @app.route("/api/comparison")
    @login_required
    def get_comparison_data():
        """API for sales vs purchase comparison."""

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))

        sales_df = load_csv_data("sales.csv", data_dir)
        if sales_df is None:
            sales_df = load_csv_data("final sale.csv", data_dir)
        purchase_df = load_csv_data("purchase.csv", data_dir)
        if purchase_df is None:
            purchase_df = load_csv_data("final purchase.csv", data_dir)

        if sales_df is None or purchase_df is None:
            return (
                jsonify(
                    {
                        "error": "Data not found",
                        "labels": ["Sales", "Purchase"],
                        "values": [0.0, 0.0],
                        "difference": 0.0,
                        "total_sales": 0.0,
                        "total_purchase": 0.0,
                    }
                ),
                404,
            )

        sales_df = normalize_sales(sales_df)
        purchase_df = normalize_purchase(purchase_df)

        if sales_df is None or purchase_df is None:
            return (
                jsonify(
                    {
                        "error": "Invalid format",
                        "labels": ["Sales", "Purchase"],
                        "values": [0.0, 0.0],
                        "difference": 0.0,
                        "total_sales": 0.0,
                        "total_purchase": 0.0,
                    }
                ),
                400,
            )

        if region:
            sales_df = sales_df[sales_df["city"].astype(str).str.lower() == region.lower()]
            if "region" in purchase_df.columns:
                purchase_df = purchase_df[purchase_df["region"].astype(str).str.lower() == region.lower()]
            else:
                purchase_df = purchase_df[purchase_df["vendor"].astype(str).str.lower() == region.lower()]

        sales_df = apply_date_range(sales_df, start_date, end_date)
        purchase_df = apply_date_range(purchase_df, start_date, end_date)

        sales_total = float(sales_df["amount"].sum()) if len(sales_df) > 0 else 0.0
        purchase_total = float(purchase_df["amount"].sum()) if len(purchase_df) > 0 else 0.0

        diff = sales_total - purchase_total
        return jsonify(
            {
                "labels": ["Sales", "Purchase"],
                "values": [sales_total, purchase_total],
                "difference": diff,
                "total_sales": sales_total,
                "total_purchase": purchase_total,
            }
        )

    @app.route("/api/insights")
    @login_required
    def get_insights():
        """API for dynamic insights."""

        region = get_filter_param("region")
        start_date = parse_date(get_filter_param("start_date"))
        end_date = parse_date(get_filter_param("end_date"))

        sales_df = load_csv_data("sales.csv", data_dir)
        if sales_df is None:
            sales_df = load_csv_data("final sale.csv", data_dir)
        purchase_df = load_csv_data("purchase.csv", data_dir)
        if purchase_df is None:
            purchase_df = load_csv_data("final purchase.csv", data_dir)

        sales_df = normalize_sales(sales_df) if sales_df is not None else None
        purchase_df = normalize_purchase(purchase_df) if purchase_df is not None else None

        if sales_df is None and purchase_df is None:
            return jsonify({"insights": ["No data available."]})

        if region:
            if sales_df is not None:
                sales_df = sales_df[sales_df["city"].astype(str).str.lower() == region.lower()]
            if purchase_df is not None:
                if "region" in purchase_df.columns:
                    purchase_df = purchase_df[purchase_df["region"].astype(str).str.lower() == region.lower()]
                else:
                    purchase_df = purchase_df[purchase_df["vendor"].astype(str).str.lower() == region.lower()]

        if sales_df is not None:
            sales_df = apply_date_range(sales_df, start_date, end_date)
        if purchase_df is not None:
            purchase_df = apply_date_range(purchase_df, start_date, end_date)

        def fmt_date(d):
            try:
                return d.strftime("%d-%m-%Y")
            except Exception:
                return str(d)

        def top_group_label_and_value(df, label_col):
            if df is None or len(df) == 0:
                return None, None
            totals = df.groupby(label_col)["amount"].sum().sort_values(ascending=False)
            if len(totals) == 0:
                return None, None
            return str(totals.index[0]), float(totals.iloc[0])

        def top_day_and_value(df):
            if df is None or len(df) == 0:
                return None, None
            day_totals = df.groupby(df["date"].dt.date)["amount"].sum().sort_values(ascending=False)
            if len(day_totals) == 0:
                return None, None
            return day_totals.index[0], float(day_totals.iloc[0])

        sales_total = float(sales_df["amount"].sum()) if sales_df is not None and len(sales_df) > 0 else 0.0
        purchase_total = (
            float(purchase_df["amount"].sum()) if purchase_df is not None and len(purchase_df) > 0 else 0.0
        )

        insights: list[str] = []

        if region:
            insights.append(f"Region filter: {region}")
        if start_date or end_date:
            sd = fmt_date(start_date) if start_date else "..."
            ed = fmt_date(end_date) if end_date else "..."
            insights.append(f"Date range: {sd} to {ed}")

        if sales_df is not None and len(sales_df) > 0:
            top_city, top_city_total = top_group_label_and_value(sales_df, "city")
            if top_city:
                insights.append(f"Top sales city: {top_city} (₹{top_city_total:,.0f})")
            best_day, best_day_total = top_day_and_value(sales_df)
            if best_day:
                insights.append(f"Best sales day: {fmt_date(best_day)} (₹{best_day_total:,.0f})")

        if purchase_df is not None and len(purchase_df) > 0:
            top_vendor, top_vendor_total = top_group_label_and_value(purchase_df, "vendor")
            if top_vendor:
                insights.append(f"Top purchase vendor: {top_vendor} (₹{top_vendor_total:,.0f})")
            best_day, best_day_total = top_day_and_value(purchase_df)
            if best_day:
                insights.append(f"Highest purchase day: {fmt_date(best_day)} (₹{best_day_total:,.0f})")

        diff = sales_total - purchase_total
        if (
            sales_df is not None
            and len(sales_df) > 0
            and purchase_df is not None
            and len(purchase_df) > 0
        ):
            margin = (diff / sales_total) * 100 if sales_total else 0.0
            if diff > 0:
                insights.append(f"Good news! Net profit ₹{diff:,.0f} (Margin {margin:.1f}%)")
            elif diff < 0:
                insights.append(f"Loss Alert: ₹{abs(diff):,.0f} (Margin {margin:.1f}%)")
            else:
                insights.append("Break-even")
        else:
            if diff > 0:
                insights.append(f"Net profit (Sales - Purchase): ₹{diff:,.0f}")
            elif diff < 0:
                insights.append(f"Net loss (Sales - Purchase): ₹{abs(diff):,.0f}")
            else:
                insights.append("Break-even")

        if not insights:
            insights = ["No insights available for selected filters."]

        return jsonify({"insights": insights})
