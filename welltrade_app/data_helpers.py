from __future__ import annotations

import os
from datetime import timedelta

import pandas as pd


def load_csv_data(filename: str, data_dir: str):
    """Load CSV data with error handling.

    Prefers /data uploads first, then falls back to project root.
    """

    try:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            filepath = filename
        return pd.read_csv(filepath, header=None)
    except FileNotFoundError:
        return None


def parse_date(value):
    """Parse date string (yyyy-mm-dd or dd-mm-yyyy)."""

    if not value:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        if len(value) >= 10 and value[4] == "-" and value[7] == "-":
            return pd.to_datetime(value, format="%Y-%m-%d")
        return pd.to_datetime(value, dayfirst=True)
    except Exception:
        return None


def normalize_sales(df: pd.DataFrame | None):
    """Normalize sales CSV: date, customer, city, amount."""

    if df is None or df.shape[1] != 4:
        return None
    df = df.copy()
    df.columns = ["date", "customer", "city", "amount"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "city", "amount"])
    return df if len(df) > 0 else None


def normalize_purchase(df: pd.DataFrame | None):
    """Normalize purchase CSV: date, vendor, [region], amount."""

    if df is None or df.shape[1] not in (3, 4):
        return None
    df = df.copy()
    if df.shape[1] == 3:
        df.columns = ["date", "vendor", "amount"]
    else:
        df.columns = ["date", "vendor", "region", "amount"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "vendor", "amount"])
    return df if len(df) > 0 else None


def apply_date_range(df: pd.DataFrame, start_date, end_date):
    """Filter by date range."""

    if start_date is not None:
        df = df[df["date"] >= start_date]
    if end_date is not None:
        df = df[df["date"] <= end_date]
    return df


def previous_period(start_date, end_date):
    """Get previous period dates."""

    duration = end_date - start_date
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - duration
    return prev_start, prev_end


def growth_pct(current: float, previous: float | None):
    """Calculate growth percentage."""

    if not previous or previous == 0:
        return None
    try:
        return round(((current - previous) / previous) * 100, 2)
    except Exception:
        return None
