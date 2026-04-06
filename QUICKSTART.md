# 🚀 Quick Start Guide - Data-Driven Dashboard

## What's New?

Your Flask dashboard has been upgraded from **static UI** to a **fully functional data-driven dashboard** with:
- ✅ Real sales & purchase CSV data (your actual files)
- ✅ Data grouped by city and vendor
- ✅ Interactive Chart.js visualizations
- ✅ Dynamic KPI metrics
- ✅ 3 API endpoints for data
- ✅ Professional styling with animations

---

## Installation & Setup (3 Steps)

### Step 1: Install pandas
```bash
pip install pandas==2.1.0
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open Browser
```
http://127.0.0.1:5000/login
```

**Demo Credentials:**
- Username: `admin` | Password: `password123`
- Username: `user` | Password: `user123`

---

## 📊 What You Can Now Do

### Dashboard (Main Hub)
- View **3 dynamic KPI cards** with real metrics
- See Total Sales, Total Purchase, Profit Margin
- Navigate to detailed analytics pages

### Sales Dashboard
- Interactive **bar chart** showing sales by city
- City-wise breakdown with color visualization
- Top performing city highlighted
- Total sales KPI card
- Real-time data from final sale.csv

### Purchase Dashboard
- Interactive **bar chart** showing purchases by vendor
- Green color scheme for visual distinction
- Purchase insights and top vendor metrics
- Real-time data from final purchase.csv

### Comparison Page
- **Doughnut chart** comparing Sales vs Purchase
- 3 KPI cards: Revenue, Cost, Profit
- Profit margin percentage calculation
- Visual distribution of business metrics

---

## 📁 New Files & Folders Created

✅ Uses your existing CSV files:
- `final sale.csv` - Your sales transaction data
- `final purchase.csv` - Your purchase transaction data

## 📝 Files Modified

```
✅ app.py                 - Added API endpoints + real data processing
✅ requirements.txt       - Added pandas dependency
✅ templates/dashboard.html      - Added KPI cards + JS
✅ templates/sales.html          - Added city chart + API call
✅ templates/purchase.html       - Added vendor chart + API call
✅ templates/comparison.html     - Added chart + API call + KPI
✅ static/css/style.css          - Added KPI + chart styling
```

---

## 🔌 API Endpoints Available

All endpoints require login. Access via browser or API calls:

**GET** `/api/sales-data`
```json
{
  "labels": ["East", "North", "South", "West"],
  "values": [100500, 95000, 80000, 85000],
  "total": 360500,
  "top_region": "East"
}
```

**GET** `/api/purchase-data`
```json
{
  "labels": ["East", "North", "South", "West"],
  "values": [52500, 47500, 40000, 42500],
  "total": 182500,
  "top_region": "East"
}
```

**GET** `/api/comparison`
```json
{
  "labels": ["Total Sales", "Total Purchase"],
  "values": [360500, 182500],
  "total_sales": 360500,
  "total_purchase": 182500,
  "difference": 178000
}
```

---

## 🎨 Chart Visualizations

| Page | Chart Type | Data Source | Color |
|------|-----------|------------|-------|
| Sales | Bar Chart | sales.csv | Blue (#3b82f6) |
| Purchase | Bar Chart | purchase.csv | Green (#10b981) |
| Comparison | Doughnut | Both CSV | Mixed |

---

## 💡 How Data Flows

```
CSV File → Pandas Process → API Endpoint → JavaScript Fetch → Chart.js → Browser Display
```

---

## 🔧 Customization Tips

### Add More Sales Data
1. Open `final sale.csv`
2. Add new rows with: `date,customer_name,city,amount`
3. Save file
4. Refresh dashboard - chart updates automatically

### Add More Purchase Data
1. Open `final purchase.csv`
2. Add new rows with: `date,vendor_name,amount`
3. Save file
4. Refresh dashboard - chart updates automatically

### Add More Metrics
1. Create new CSV files in `data/` folder
2. Add new function in `app.py` to process the data
3. Create new API endpoint
4. Update HTML template with new chart

---

## ❓ Troubleshooting

**"Data not found" error?**
- Ensure `data/sales.csv` and `data/purchase.csv` exist
- Check file locations and names (case-sensitive on Linux)

**Charts not showing?**
- Open browser DevTools (F12) → Console
- Check for validation errors
- Verify pandas is installed: `pip list | grep pandas`

**Login issues?**
- Clear browser cookies
- Use demo credentials: admin / password123

---

## 📊 Sample Data Info

**Data Format - Sales:**
```
date,customer_name,city,amount
01-04-2024,SAI MEDICAL STORE (NEW),SURAT,6720.00
01-04-2024,SHREE HARI SURGICAL,SURAT,4831.00
```

**Data Format - Purchase:**
```
date,vendor_name,amount
01-04-2024,KAVYA DISTRIBUTORS,6160.00
01-04-2024,UDAY SURGIPHARMA(P),5600.00
```

**Cities in Your Data:**
- SURAT (1st in sales)
- VALSAD
- ANAND
- VAPI
- NAVSARI
- ANKLESHWAR
- AHEMEDABAD
- VYARA

**Vendors in Your Data:**
- ALPHA MEDICARE AND DEVICES PVT.LTD.
- SHAYONA INC.(INDIA)
- ASTRID HEALTHCARE LLP
- PRANAV ENTERPRISE
- And 40+ more vendors...

---

## ✅ Features Checklist

- [x] CSV data loading
- [x] Backend API endpoints
- [x] Frontend chart integration
- [x] Dynamic KPI cards
- [x] Currency formatting
- [x] Responsive design
- [x] Error handling
- [x] Professional styling
- [x] Authentication required
- [x] Real-time JSON responses

---

## 🎯 Next Steps

1. **Test Everything** - Login and navigate all dashboards
2. **Update CSV Data** - Replace sample data with real data
3. **Monitor Charts** - Verify all visualizations load correctly
4. **Customize Colors** - Match your brand guidelines
5. **Deploy** - When ready, deploy to production

---

## 📚 Documentation

For complete details, see: `DASHBOARD_IMPLEMENTATION.md`

**Status:** ✅ **READY TO USE**

---

*Your data-driven dashboard is now LIVE! 🎉*
