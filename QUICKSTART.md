# 🚀 Quick Start Guide - Welltrade Surgipharma Dashboard

This guide is kept in sync with the current codebase (SQLite login + CSV analytics + prediction).

---

## ✅ Prerequisites

- **Python 3.12** recommended (fastest install experience on Windows)
- Git (optional, only if you want to clone)

---

## ⚡ Setup (Windows PowerShell)

### 1) Create + Activate Virtual Environment
```bash
py -3.12 -m venv .venv
.\.venv\Scripts\activate
```

### 2) Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3) Run the App
```bash
python app.py
```

### 4) Open in Browser
- `http://127.0.0.1:5000/login`

---

## 🔐 Demo Login (Auto-Created)

On first run, the app creates `app.db` and inserts demo users.

- **Admin**: `admin@gmail.com` / `1234`
- **Manager**: `manager@gmail.com` / `1234`

---

## 📊 What You Can Do

- **Dashboard**: KPI cards + charts
- **Sales / Purchase**: analytics charts (Chart.js)
- **Comparison**: Sales vs Purchase totals
- **Prediction**: forecasts next **3–4 months** using a simple straight-line trend; includes **Download CSV** button
- **Reports**: upload/download/delete PDFs (admin only)

---

## 📁 Data Files Used

Primary files (recommended):
- `data/sales.csv`
- `data/purchase.csv`

Fallback (if the above are missing):
- `final sale.csv`
- `final purchase.csv`

---

## 🧾 CSV Format (Upload)

Sales CSV columns (exactly 4):
```
date,customer_name,city,amount
```

Purchase CSV columns (3 or 4):
```
date,vendor_name,amount
```
or
```
date,vendor_name,region,amount
```

---

## ❓ Troubleshooting

**App won’t start / missing packages**
- Make sure `.venv` is activated, then reinstall: `python -m pip install -r requirements.txt`

**Charts show “No data”**
- Confirm `data/sales.csv` and `data/purchase.csv` exist (or the `final *.csv` fallback files exist)

**Login not working**
- Use: `admin@gmail.com / 1234`
- If you changed users before, delete `app.db` (optional) and run the app again to recreate defaults

---

## 📚 More Details

See `DASHBOARD_IMPLEMENTATION.md` for deeper implementation notes.
