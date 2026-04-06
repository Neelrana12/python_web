"""
WELLTRADE SURGIPHARMA - ANALYTICS DASHBOARD (SIMPLIFIED)

MAIN FEATURES:
- Login (admin/manager)
- Charts (sales, purchase, comparison)
- Filters (region + date)
- Growth %
- Insights
- Upload/Download/Delete files
"""

from __future__ import annotations

import os
from datetime import timedelta
from functools import wraps

import pandas as pd
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from db import ensure_default_admin, get_user_by_email, init_db, verify_password


# ========================
# SETUP
# ========================

app = Flask(__name__)
app.secret_key = "welltrade-secret-2024"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

MAX_UPLOAD_MB = 10
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

ALLOWED_REPORT_EXTENSIONS = {'.pdf'}

init_db()
ensure_default_admin()


@app.errorhandler(413)
def file_too_large(_e):
    return f"File too large. Max {MAX_UPLOAD_MB}MB.", 413


# ========================
# AUTH DECORATORS
# ========================

def login_required(func):
    """User must be logged in"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """User must be admin"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            return "Forbidden", 403
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# Step 4A: Data Loading Functions
# ==========================================

def load_csv_data(filename):
    """Load CSV data with error handling"""
    try:
        # Prefer /data uploads first, then fallback to project root.
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            filepath = filename
        
        # For sales: date, customer_name, city, amount
        # For purchase: date, vendor_name, amount
        df = pd.read_csv(filepath, header=None)
        return df
    except FileNotFoundError:
        return None

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def parse_date(value):
    """Parse date string (yyyy-mm-dd or dd-mm-yyyy)"""
    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    # Try format detection
    try:
        if len(value) >= 10 and value[4] == '-' and value[7] == '-':
            return pd.to_datetime(value, format='%Y-%m-%d')
        else:
            return pd.to_datetime(value, dayfirst=True)
    except:
        return None

def normalize_sales(df):
    """Normalize sales CSV: date, customer, city, amount"""
    if df is None or df.shape[1] != 4:
        return None
    df = df.copy()
    df.columns = ['date', 'customer', 'city', 'amount']
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['date', 'city', 'amount'])
    return df if len(df) > 0 else None

def normalize_purchase(df):
    """Normalize purchase CSV: date, vendor, [region], amount"""
    if df is None or df.shape[1] not in (3, 4):
        return None
    df = df.copy()
    if df.shape[1] == 3:
        df.columns = ['date', 'vendor', 'amount']
    else:
        df.columns = ['date', 'vendor', 'region', 'amount']
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['date', 'vendor', 'amount'])
    return df if len(df) > 0 else None

def apply_date_range(df, start_date, end_date):
    """Filter by date range"""
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    return df

def previous_period(start_date, end_date):
    """Get previous period dates"""
    duration = end_date - start_date
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - duration
    return prev_start, prev_end

def growth_pct(current, previous):
    """Calculate growth percentage"""
    if not previous or previous == 0:
        return None
    try:
        return round(((current - previous) / previous) * 100, 2)
    except:
        return None

def get_username():
    """Get current username"""
    return session.get('username') or session.get('email')

def get_filter_param(param_name, default=''):
    """Get filter from URL param or session"""
    value = request.args.get(param_name, '').strip()
    if value:
        return value
    gf = session.get('global_filters') or {}
    if param_name == 'region':
        return session.get('region_filter') or gf.get('region', '')
    elif param_name == 'start_date':
        return session.get('start_date_filter') or gf.get('start_date', '')
    elif param_name == 'end_date':
        return session.get('end_date_filter') or gf.get('end_date', '')
    return default

def validate_csv(uploaded_file):
    """Check if file is valid text CSV"""
    if not hasattr(uploaded_file, 'stream'):
        return False
    try:
        uploaded_file.stream.seek(0)
        header = uploaded_file.stream.read(2)
        uploaded_file.stream.seek(0)
        return all(isinstance(b, int) and (32 <= b <= 126 or b in (9, 10, 13)) for b in header)
    except:
        return True

def validate_pdf(uploaded_file):
    """Check if file is valid PDF"""
    if not hasattr(uploaded_file, 'stream'):
        return False
    try:
        uploaded_file.stream.seek(0)
        header = uploaded_file.stream.read(4)
        uploaded_file.stream.seek(0)
        return header.startswith(b'%PDF')
    except:
        return False

# ==========================================
# API ENDPOINTS
# ==========================================

@app.route('/api/sales-data')
@login_required
def get_sales_data():
    """API for sales by city"""
    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))
    top_n = int(request.args.get('top_n', 10))

    # Load and normalize data
    df = load_csv_data('sales.csv')
    if df is None:
        df = load_csv_data('final sale.csv')
    if df is None:
        return jsonify({'error': 'Sales data not found', 'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'top_n': top_n, 'growth_pct': None}), 404
    
    df = normalize_sales(df)
    if df is None:
        return jsonify({'error': 'Invalid format', 'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'top_n': top_n, 'growth_pct': None}), 400
    
    # Filter by region
    if region:
        df = df[df['city'].astype(str).str.lower() == region.lower()]

    # Keep a copy for growth calculation (region-filtered, not date-filtered)
    df_for_growth = df

    # Filter by date
    df = apply_date_range(df, start_date, end_date)
    
    # Get top N by city
    if len(df) == 0:
        return jsonify({'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'growth_pct': None})
    
    city_totals = df.groupby('city')['amount'].sum().sort_values(ascending=False)
    all_total = city_totals.sum()
    top_cities = city_totals.head(top_n)
    
    # Calculate growth
    growth = None
    if len(df_for_growth) > 0:
        if start_date and end_date:
            current_total = float(all_total)
            prev_start, prev_end = previous_period(start_date, end_date)
        else:
            # Default to a rolling 30-day window so growth isn't N/A by default
            auto_end = df_for_growth['date'].max()
            auto_start = auto_end - timedelta(days=29)
            df_current = apply_date_range(df_for_growth, auto_start, auto_end)
            current_total = float(df_current['amount'].sum()) if len(df_current) > 0 else 0.0
            prev_start, prev_end = previous_period(auto_start, auto_end)

        df_prev = apply_date_range(df_for_growth, prev_start, prev_end)
        prev_total = float(df_prev['amount'].sum()) if len(df_prev) > 0 else 0.0
        growth = growth_pct(current_total, prev_total)

    return jsonify({
        'labels': top_cities.index.tolist(),
        'values': [float(v) for v in top_cities.values.tolist()],
        'total': float(all_total),
        'top_region': top_cities.index[0] if len(top_cities) > 0 else 'N/A',
        'top_n': top_n,
        'growth_pct': growth
    })

@app.route('/api/predict-sales')
@login_required
def api_predict_sales():
    """Predict next 3–4 months sales using average monthly growth (no ML)."""
    # Months to predict (kept short + exam-friendly)
    try:
        months_ahead = int(request.args.get('months', 3))
    except:
        months_ahead = 3
    months_ahead = max(3, min(months_ahead, 4))

    # Optional global filters from header
    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))

    df = load_csv_data('sales.csv')
    if df is None:
        df = load_csv_data('final sale.csv')
    df = normalize_sales(df) if df is not None else None
    if df is None or len(df) == 0:
        return jsonify({'months': [], 'predictions': []})

    if region:
        df = df[df['city'].astype(str).str.lower() == region.lower()]
    df = apply_date_range(df, start_date, end_date)
    if df is None or len(df) == 0:
        return jsonify({'months': [], 'predictions': []})

    # 1) Convert to monthly totals
    monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().sort_index()
    last_value = float(monthly.iloc[-1])

    # 2) Average monthly growth (use recent months for stability)
    recent = monthly.tail(6)
    diffs = recent.diff().dropna()
    avg_growth = float(diffs.mean()) if len(diffs) > 0 else 0.0

    # 3) Predict next months: last_value + avg_growth * i
    last_period = monthly.index[-1]
    months = []
    predictions = []
    for i in range(1, months_ahead + 1):
        next_period = last_period + i
        months.append(next_period.to_timestamp().strftime('%b %Y'))
        predictions.append(max(0.0, last_value + avg_growth * i))

    return jsonify({'months': months, 'predictions': [float(v) for v in predictions]})

@app.route('/api/predict-purchase')
@login_required
def api_predict_purchase():
    """Predict next 3–4 months purchase using average monthly growth (no ML)."""
    try:
        months_ahead = int(request.args.get('months', 3))
    except:
        months_ahead = 3
    months_ahead = max(3, min(months_ahead, 4))

    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))

    df = load_csv_data('purchase.csv')
    if df is None:
        df = load_csv_data('final purchase.csv')
    df = normalize_purchase(df) if df is not None else None
    if df is None or len(df) == 0:
        return jsonify({'months': [], 'predictions': []})

    # Optional region/vendor filter (mirrors existing purchase endpoint behavior)
    if region:
        if 'region' in df.columns:
            df = df[df['region'].astype(str).str.lower() == region.lower()]
        else:
            df = df[df['vendor'].astype(str).str.lower() == region.lower()]

    df = apply_date_range(df, start_date, end_date)
    if df is None or len(df) == 0:
        return jsonify({'months': [], 'predictions': []})

    monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().sort_index()
    last_value = float(monthly.iloc[-1])

    recent = monthly.tail(6)
    diffs = recent.diff().dropna()
    avg_growth = float(diffs.mean()) if len(diffs) > 0 else 0.0

    last_period = monthly.index[-1]
    months = []
    predictions = []
    for i in range(1, months_ahead + 1):
        next_period = last_period + i
        months.append(next_period.to_timestamp().strftime('%b %Y'))
        predictions.append(max(0.0, last_value + avg_growth * i))

    return jsonify({'months': months, 'predictions': [float(v) for v in predictions]})


@app.route('/api/purchase-data')
@login_required
def get_purchase_data():
    """API for purchase by vendor"""
    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))
    top_n = int(request.args.get('top_n', 10))

    # Load and normalize data
    df = load_csv_data('purchase.csv')
    if df is None:
        df = load_csv_data('final purchase.csv')
    if df is None:
        return jsonify({'error': 'Purchase data not found', 'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'top_n': top_n, 'growth_pct': None}), 404
    
    df = normalize_purchase(df)
    if df is None:
        return jsonify({'error': 'Invalid format', 'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'top_n': top_n, 'growth_pct': None}), 400
    
    # Filter by region/vendor
    if region:
        if 'region' in df.columns:
            df = df[df['region'].astype(str).str.lower() == region.lower()]
        else:
            df = df[df['vendor'].astype(str).str.lower() == region.lower()]

    # Keep a copy for growth calculation (region-filtered, not date-filtered)
    df_for_growth = df
    
    # Filter by date
    df = apply_date_range(df, start_date, end_date)
    
    # Get top N by vendor
    if len(df) == 0:
        return jsonify({'labels': [], 'values': [], 'total': 0, 'top_region': 'N/A', 'growth_pct': None})
    
    vendor_totals = df.groupby('vendor')['amount'].sum().sort_values(ascending=False)
    all_total = vendor_totals.sum()
    top_vendors = vendor_totals.head(top_n)
    
    # Calculate growth
    growth = None
    if len(df_for_growth) > 0:
        if start_date and end_date:
            current_total = float(all_total)
            prev_start, prev_end = previous_period(start_date, end_date)
        else:
            # Default to a rolling 30-day window so growth isn't N/A by default
            auto_end = df_for_growth['date'].max()
            auto_start = auto_end - timedelta(days=29)
            df_current = apply_date_range(df_for_growth, auto_start, auto_end)
            current_total = float(df_current['amount'].sum()) if len(df_current) > 0 else 0.0
            prev_start, prev_end = previous_period(auto_start, auto_end)

        df_prev = apply_date_range(df_for_growth, prev_start, prev_end)
        prev_total = float(df_prev['amount'].sum()) if len(df_prev) > 0 else 0.0
        growth = growth_pct(current_total, prev_total)
    
    return jsonify({
        'labels': top_vendors.index.tolist(),
        'values': [float(v) for v in top_vendors.values.tolist()],
        'total': float(all_total),
        'top_region': top_vendors.index[0] if len(top_vendors) > 0 else 'N/A',
        'top_n': top_n,
        'growth_pct': growth
    })

@app.route('/api/comparison')
@login_required
def get_comparison_data():
    """API for sales vs purchase comparison"""
    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))

    # Load data
    sales_df = load_csv_data('sales.csv')
    if sales_df is None:
        sales_df = load_csv_data('final sale.csv')
    purchase_df = load_csv_data('purchase.csv')
    if purchase_df is None:
        purchase_df = load_csv_data('final purchase.csv')

    if sales_df is None or purchase_df is None:
        return jsonify({'error': 'Data not found', 'labels': ['Sales', 'Purchase'], 'values': [0.0, 0.0], 'difference': 0.0, 'total_sales': 0.0, 'total_purchase': 0.0}), 404
    
    # Normalize
    sales_df = normalize_sales(sales_df)
    purchase_df = normalize_purchase(purchase_df)
    
    if sales_df is None or purchase_df is None:
        return jsonify({'error': 'Invalid format', 'labels': ['Sales', 'Purchase'], 'values': [0.0, 0.0], 'difference': 0.0, 'total_sales': 0.0, 'total_purchase': 0.0}), 400
    
    # Filter by region
    if region:
        sales_df = sales_df[sales_df['city'].astype(str).str.lower() == region.lower()]
        if 'region' in purchase_df.columns:
            purchase_df = purchase_df[purchase_df['region'].astype(str).str.lower() == region.lower()]
        else:
            purchase_df = purchase_df[purchase_df['vendor'].astype(str).str.lower() == region.lower()]
    
    # Filter by date
    sales_df = apply_date_range(sales_df, start_date, end_date)
    purchase_df = apply_date_range(purchase_df, start_date, end_date)
    
    # Totals
    sales_total = float(sales_df['amount'].sum()) if len(sales_df) > 0 else 0.0
    purchase_total = float(purchase_df['amount'].sum()) if len(purchase_df) > 0 else 0.0
    
    diff = sales_total - purchase_total
    return jsonify({
        'labels': ['Sales', 'Purchase'],
        'values': [sales_total, purchase_total],
        'difference': diff,
        'total_sales': sales_total,
        'total_purchase': purchase_total,
    })

@app.route('/api/insights')
@login_required
def get_insights():
    """API for dynamic insights"""
    region = get_filter_param('region')
    start_date = parse_date(get_filter_param('start_date'))
    end_date = parse_date(get_filter_param('end_date'))

    # Load data
    sales_df = load_csv_data('sales.csv')
    if sales_df is None:
        sales_df = load_csv_data('final sale.csv')
    purchase_df = load_csv_data('purchase.csv')
    if purchase_df is None:
        purchase_df = load_csv_data('final purchase.csv')
    
    # Normalize
    sales_df = normalize_sales(sales_df) if sales_df is not None else None
    purchase_df = normalize_purchase(purchase_df) if purchase_df is not None else None
    
    if sales_df is None and purchase_df is None:
        return jsonify({'insights': ['No data available.']})
    
    # Filter by region
    if region:
        if sales_df is not None:
            sales_df = sales_df[sales_df['city'].astype(str).str.lower() == region.lower()]
        if purchase_df is not None:
            if 'region' in purchase_df.columns:
                purchase_df = purchase_df[purchase_df['region'].astype(str).str.lower() == region.lower()]
            else:
                purchase_df = purchase_df[purchase_df['vendor'].astype(str).str.lower() == region.lower()]
    
    # Filter by date
    if sales_df is not None:
        sales_df = apply_date_range(sales_df, start_date, end_date)
    if purchase_df is not None:
        purchase_df = apply_date_range(purchase_df, start_date, end_date)
    
    def fmt_date(d):
        try:
            return d.strftime('%d-%m-%Y')
        except Exception:
            return str(d)

    def top_group_label_and_value(df, label_col):
        if df is None or len(df) == 0:
            return None, None
        totals = df.groupby(label_col)['amount'].sum().sort_values(ascending=False)
        if len(totals) == 0:
            return None, None
        return str(totals.index[0]), float(totals.iloc[0])

    def top_day_and_value(df):
        if df is None or len(df) == 0:
            return None, None
        # Group by calendar date (ignore time)
        day_totals = df.groupby(df['date'].dt.date)['amount'].sum().sort_values(ascending=False)
        if len(day_totals) == 0:
            return None, None
        return day_totals.index[0], float(day_totals.iloc[0])

    # Calculate totals
    sales_total = float(sales_df['amount'].sum()) if sales_df is not None and len(sales_df) > 0 else 0.0
    purchase_total = float(purchase_df['amount'].sum()) if purchase_df is not None and len(purchase_df) > 0 else 0.0

    insights: list[str] = []

    # Optional: show applied filters (keeps UI same, only text)
    if region:
        insights.append(f"Region filter: {region}")
    if start_date or end_date:
        sd = fmt_date(start_date) if start_date else '...'
        ed = fmt_date(end_date) if end_date else '...'
        insights.append(f"Date range: {sd} to {ed}")

    # Sales insights
    if sales_df is not None and len(sales_df) > 0:
        top_city, top_city_total = top_group_label_and_value(sales_df, 'city')
        if top_city:
            insights.append(f"Top sales city: {top_city} (₹{top_city_total:,.0f})")
        best_day, best_day_total = top_day_and_value(sales_df)
        if best_day:
            insights.append(f"Best sales day: {fmt_date(best_day)} (₹{best_day_total:,.0f})")

    # Purchase insights
    if purchase_df is not None and len(purchase_df) > 0:
        top_vendor, top_vendor_total = top_group_label_and_value(purchase_df, 'vendor')
        if top_vendor:
            insights.append(f"Top purchase vendor: {top_vendor} (₹{top_vendor_total:,.0f})")
        best_day, best_day_total = top_day_and_value(purchase_df)
        if best_day:
            insights.append(f"Highest purchase day: {fmt_date(best_day)} (₹{best_day_total:,.0f})")

    # Profit / loss summary
    diff = sales_total - purchase_total
    if sales_df is not None and len(sales_df) > 0 and purchase_df is not None and len(purchase_df) > 0:
        margin = (diff / sales_total) * 100 if sales_total else 0.0
        if diff > 0:
            insights.append(f"Good news! Net profit ₹{diff:,.0f} (Margin {margin:.1f}%)")
        elif diff < 0:
            insights.append(f"Loss Alert: ₹{abs(diff):,.0f} (Margin {margin:.1f}%)")
        else:
            insights.append("Break-even")
    else:
        # Keep at least one business summary line even if one dataset missing
        if diff > 0:
            insights.append(f"Net profit (Sales - Purchase): ₹{diff:,.0f}")
        elif diff < 0:
            insights.append(f"Net loss (Sales - Purchase): ₹{abs(diff):,.0f}")
        else:
            insights.append("Break-even")

    # Ensure non-empty list (UI expects an array)
    if not insights:
        insights = ['No insights available for selected filters.']

    return jsonify({'insights': insights})

@app.route('/upload', methods=['POST'])
@admin_required
def upload():
    """Admin-only: upload CSV (sales/purchase) and PDF reports."""
    upload_kind = (request.form.get('upload_kind') or '').strip().lower()
    uploaded_file = request.files.get('file')

    if upload_kind not in {'sales_csv', 'purchase_csv', 'report_pdf'}:
        return "Invalid upload_kind", 400
    if not uploaded_file or not uploaded_file.filename:
        return "No file uploaded", 400

    original_name = uploaded_file.filename
    ext = os.path.splitext(original_name)[1].lower()

    # Handle CSV uploads
    if upload_kind in {'sales_csv', 'purchase_csv'}:
        if ext != '.csv':
            return "Only .csv files allowed", 400
        if not validate_csv(uploaded_file):
            return "Invalid CSV file", 400
        
        # Validate column count
        try:
            df = pd.read_csv(uploaded_file, header=None)
            uploaded_file.stream.seek(0)
        except Exception:
            return "Invalid CSV file", 400
        
        col_count = df.shape[1]
        if upload_kind == 'sales_csv' and col_count != 4:
            return "Sales CSV must have 4 columns: date, customer, city, amount", 400
        if upload_kind == 'purchase_csv' and col_count not in (3, 4):
            return "Purchase CSV must have 3-4 columns", 400
        
        # Save
        target_name = 'sales.csv' if upload_kind == 'sales_csv' else 'purchase.csv'
        target_path = os.path.join(DATA_DIR, secure_filename(target_name))
        uploaded_file.save(target_path)
        return redirect(url_for('sales' if upload_kind == 'sales_csv' else 'purchase'))

    # Handle PDF uploads
    if ext not in ALLOWED_REPORT_EXTENSIONS:
        return "Only PDF reports allowed", 400
    if not validate_pdf(uploaded_file):
        return "Invalid PDF file", 400

    # Save with auto-numbering if exists
    safe_name = secure_filename(original_name)
    if not safe_name.lower().endswith('.pdf'):
        safe_name = safe_name + '.pdf'
    
    target_path = os.path.join(REPORTS_DIR, safe_name)
    if os.path.exists(target_path):
        base, _ = os.path.splitext(safe_name)
        counter = 1
        while os.path.exists(os.path.join(REPORTS_DIR, f"{base}-{counter}.pdf")):
            counter += 1
        target_path = os.path.join(REPORTS_DIR, f"{base}-{counter}.pdf")
    
    uploaded_file.save(target_path)
    return redirect(url_for('reports'))


# ==========================================
# FILE MANAGEMENT ROUTES
# ==========================================

@app.route('/reports')
@login_required
def reports():
    """Report library: list PDF reports (admin + manager)."""
    files = []
    try:
        for name in os.listdir(REPORTS_DIR):
            if name.lower().endswith('.pdf'):
                files.append(name)
    except FileNotFoundError:
        files = []

    files.sort(key=lambda x: x.lower())
    return render_template('reports.html', username=get_username(), files=files)


@app.route('/download/<path:filename>')
@login_required
def download(filename: str):
    """Download a PDF report (admin + manager)."""
    safe_name = secure_filename(filename)
    if not safe_name.lower().endswith('.pdf'):
        abort(404)
    full_path = os.path.join(REPORTS_DIR, safe_name)
    if not os.path.exists(full_path):
        abort(404)
    return send_from_directory(REPORTS_DIR, safe_name, as_attachment=True)


@app.route('/reports/delete/<path:filename>', methods=['POST'])
@admin_required
def delete_report(filename: str):
    """Admin-only: delete a PDF report from the report library."""
    safe_name = secure_filename(filename)
    if not safe_name.lower().endswith('.pdf'):
        abort(404)

    full_path = os.path.join(REPORTS_DIR, safe_name)
    if not os.path.exists(full_path):
        abort(404)

    try:
        os.remove(full_path)
    except Exception:
        return "Failed to delete report", 500

    return redirect(url_for('reports'))




@app.route('/global-filter', methods=['POST'])
@login_required
def set_global_filter():
    """Set global region/date filters in session"""
    region = (request.form.get('region') or '').strip()
    start_date = (request.form.get('start_date') or '').strip()
    end_date = (request.form.get('end_date') or '').strip()
    session['region_filter'] = region
    session['start_date_filter'] = start_date
    session['end_date_filter'] = end_date
    session['global_filters'] = {'region': region, 'start_date': start_date, 'end_date': end_date}
    return redirect(request.form.get('next') or url_for('dashboard'))

@app.route('/global-filter/clear', methods=['POST'])
@login_required
def clear_global_filter():
    """Clear session filters"""
    session.pop('region_filter', None)
    session.pop('start_date_filter', None)
    session.pop('end_date_filter', None)
    session.pop('global_filters', None)
    return redirect(request.form.get('next') or url_for('dashboard'))

# ==========================================
# DASHBOARD ROUTES (Pages)
# ==========================================

@app.route('/')
def home():
    """Home page - redirect based on login status"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = (request.form.get('username') or '').strip().lower()
        password = request.form.get('password') or ''

        user = get_user_by_email(email)
        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            session['username'] = user['email']
            session.permanent = True
            return redirect(url_for('dashboard'))

        error = 'Invalid email or password'
        return render_template('login.html', error=error)
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout - clear session"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', username=get_username())


@app.route('/sales')
@login_required
def sales():
    """Sales Dashboard"""
    return render_template('sales.html', username=get_username())


@app.route('/purchase')
@login_required
def purchase():
    """Purchase Dashboard"""
    return render_template('purchase.html', username=get_username())


@app.route('/comparison')
@login_required
def comparison():
    """Sales vs Purchase Comparison"""
    return render_template('comparison.html', username=get_username())


@app.route('/prediction')
@login_required
def prediction():
    """Predictive analysis page"""
    return render_template('prediction.html', username=get_username())

# ==========================================
# APPLICATION STARTUP
# ==========================================

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Start Flask server in debug mode
    app.run(debug=True, port=5000)
