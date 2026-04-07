# Welltrade Surgipharma - Analytics Dashboard

A beginner-friendly Flask analytics dashboard for pharma business data (Sales, Purchase, Comparison, Prediction) with login and PDF reports.

## ✨ Key Features

### 📊 Executive Dashboard
- Real-time KPI cards (Sales, Purchase, Profit Margin)
- Dynamic insights based on filtered data
- Growth percentage calculations
- Responsive layout for all devices

### 📈 Sales Analytics
- Sales breakdown by city/region
- Real-time charts using Chart.js
- Top performers tracking
- Growth rate metrics
- Interactive filtering

### 🛒 Purchase Insights
- Purchase data by vendor
- Supplier performance analysis
- Real-time data visualization
- Multi-vendor comparison
- Cost tracking

### 📊 Comparative Analysis
- Sales vs Purchase comparison
- Profit/Loss margins
- Trend analysis
- Period-over-period growth
- Business insights

### 🔮 Predictive Analysis (Simple + Exam-Friendly)
- Forecasts next 3–4 months for Sales and Purchase
- Uses monthly totals + a straight-line trend (Linear Regression)
- Shows **Historical vs Forecast** chart
- Download prediction as **CSV** from the Prediction page

### 📁 Reports Management
- PDF report upload/download
- Admin-controlled report library
- Secure file storage
- Auto-numbering for duplicate reports

### 🔐 Authentication
- Email/password login (bcrypt hashing)
- Admin & Manager roles
- Session management (24-hour timeout)
- SQLite database (`app.db`)

### 🎨 Professional UI
- Clean, modern SaaS design
- Responsive mobile-friendly layout
- Smooth animations & transitions
- Consistent color scheme (#4f46e5 Indigo)
- Light theme with professional shadows

## 🛠️ Tech Stack

- **Backend**: Flask
- **Local Python**: Python 3.12 (recommended for easy installs)
- **Deployment Runtime**: Python 3.11.7 (see runtime.txt)
- **Database**: SQLite + bcrypt authentication
- **Frontend**: HTML5, Jinja2 Templates, CSS3
- **Charts**: Chart.js for data visualization
- **Data Processing**: Pandas for CSV parsing
- **Icons**: FontAwesome 6.5.1
- **Deployment**: Render + Gunicorn

## 📦 Requirements

All dependencies are pinned in requirements.txt.

## 🚀 Quick Start (Local)

### 1. Clone Repository
```bash
git clone https://github.com/Neelrana12/python_web.git
cd python_web
```

### 2. Create Virtual Environment (Recommended)

Windows (PowerShell):
```bash
py -3.12 -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run Application
```bash
python app.py
```

### 5. Open in Browser
Navigate to:
- `http://127.0.0.1:5000/login`

### 6. Login with Demo Credentials
- **Admin**: admin@gmail.com / 1234
- **Manager**: manager@gmail.com / 1234

## 📁 Project Structure

```
python_web/
├── app.py                       # Entry-point (creates Flask app)
├── welltrade_app/               # All routes + helpers (modular package)
├── db.py                        # Database functions & auth
├── requirements.txt             # Python dependencies
├── Procfile                     # Render deployment config
├── runtime.txt                  # Python version
├── app.db                       # SQLite database
├── data/
│   ├── sales.csv               # Sales data (date, customer, city, amount)
│   └── purchase.csv            # Purchase data (date, vendor, [region], amount)
├── reports/                     # PDF reports storage
├── templates/
│   ├── base.html               # Base layout template
│   ├── login.html              # Login page
│   ├── dashboard.html          # Main dashboard with KPIs
│   ├── sales.html              # Sales analytics
│   ├── purchase.html           # Purchase analytics
│   ├── comparison.html         # Sales vs Purchase
│   ├── prediction.html         # Predictive analysis
│   └── reports.html            # Report library
├── static/
│   ├── css/
│   │   └── style.css           # Professional styling
│   └── images/
│       ├── logo.png            # Company logo
│       └── loginimg.png        # Login page image
└── .gitignore                   # Git ignore rules
```

## 🔐 Login System

### Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@gmail.com | 1234 |
| Manager | manager@gmail.com | 1234 |

### Database
- SQLite database (`app.db`)
- Bcrypt password hashing
- Users table with email, hashed_password, role

## 📊 API Endpoints

### Authentication
| Route | Method | Description |
|-------|--------|-------------|
| `/login` | GET, POST | Login page |
| `/logout` | GET | Logout & clear session |

### Dashboard & Navigation
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home (redirects to dashboard if logged in) |
| `/dashboard` | GET | Main dashboard with KPIs |

### Data & Analytics
| Route | Method | Description |
|-------|--------|-------------|
| `/sales` | GET | Sales dashboard |
| `/purchase` | GET | Purchase analytics |
| `/comparison` | GET | Sales vs Purchase comparison |
| `/prediction` | GET | Predictive analysis (3–4 months) |
| `/reports` | GET | PDF report library |

### API Endpoints (JSON)
| Route | Method | Description |
|-------|--------|-------------|
| `/api/sales-data` | GET | Sales data by city |
| `/api/purchase-data` | GET | Purchase data by vendor |
| `/api/comparison` | GET | Sales vs Purchase totals |
| `/api/insights` | GET | Dynamic business insights |
| `/api/predict-sales` | GET | Sales forecast (3–4 months) |
| `/api/predict-purchase` | GET | Purchase forecast (3–4 months) |

### File Management
| Route | Method | Description |
|-------|--------|-------------|
| `/upload` | POST | Upload CSV/PDF (Admin only) |
| `/download/<filename>` | GET | Download PBIX (static/reports) or PDF (reports) |
| `/reports/delete/<filename>` | POST | Delete report (Admin only) |

### Filters
| Route | Method | Description |
|-------|--------|-------------|
| `/global-filter` | POST | Set region/date filters |
| `/global-filter/clear` | POST | Clear all filters |

## 🎨 Design Features

### Color Palette (SaaS Professional)
- **Primary**: #4f46e5 (Indigo)
- **Sidebar**: #1f2937 (Dark Gray)
- **Background**: #f8fafc (Light Gray)
- **Cards**: White with soft shadows
- **Accents**: Green (#22c55e), Orange (#f59e0b)

### UI Components
- **Cards**: White with colored left borders (KPIs)
- **Buttons**: Indigo with hover scale effect (1.03)
- **Shadows**: Soft `0 8px 18px rgba(0,0,0,0.06)`
- **Transitions**: Smooth 0.3s animations
- **Gradients**: Soft pastel info cards

### Responsive Design
- Mobile-first approach
- Flexbox layouts
- Tablet & desktop optimized
- Touch-friendly navigation

## 📊 Data Format

### Sales CSV
```
date, customer_name, city, amount
2024-01-15, John Supplier, Mumbai, 50000
2024-01-16, ABC Corp, Delhi, 75000
```

### Purchase CSV
```
date, vendor_name, region, amount
2024-01-15, Vendor A, North, 30000
2024-01-16, Vendor B, South, 45000
```

## 🔮 Predictive Analysis Logic (Simple)

**Method**: Monthly totals + straight-line trend

1. Convert daily rows into **monthly total sales/purchase**
2. Fit a straight line: $y = a + b x$
3. Predict next 3–4 months from that line

This is intentionally simple and easy to explain in exams.

## 📍 Contact / Address

- **Phone**: +91 9610331100
- **Email**: welltradesurgipharma@gmail.com
- **Address**: A\94, Ruapl Industrial\1, Udhna, 52, Udhna Magdalla Road, Ground, Surat, Gujarat 394210

## 🌐 Live Deployment

- **URL**: https://corebuilds.me
- **Platform**: Render
- **Runtime**: Python 3.11.7
- **Server**: Gunicorn (WSGI)
- **Domain**: Custom domain via Render

## 🚀 Deployment Steps

### On Render.com
1. Connect GitHub repository
2. Create new Web Service
3. Set runtime: Python 3.11.7
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Add environment variables (if needed)
7. Connect custom domain

### Deploy Latest Changes
```bash
git add -A
git commit -m "Update message"
git push origin main
```
Render automatically deploys on push!

## 🔧 Configuration

### Environment
- **Debug**: False (production)
- **Port**: 5000 (local) / Auto (Render)
- **Session Timeout**: 24 hours
- **Max Upload Size**: 10 MB

### Security
- Bcrypt password hashing
- Session-based authentication
- CSRF protection via Werkzeug
- SQLite with secure queries
- No SQL injection vulnerabilities

## 📝 Code Quality

- **Language**: Python 3.11 (PEP 8 compliant)
- **Style**: Clean, readable, well-commented
- **Performance**: Optimized Pandas operations
- **Testing**: Production-ready code
- **Maintainability**: Simple logic, no external ML libraries

## 🐛 Troubleshooting

### Port Already in Use
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CSV Not Uploading
- Ensure CSV has correct columns
- Verify file is not corrupted
- Check file permissions

### Charts Not Displaying
- Check browser console for errors
- Ensure Chart.js is loaded
- Verify API endpoint returns data

## 📚 Learning Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Pandas Guide: https://pandas.pydata.org/docs/
- Chart.js Docs: https://www.chartjs.org/docs/
- Render Docs: https://render.com/docs

## 🤝 Contributing

This is a student project created for learning purposes. Feel free to fork and customize!

## 📄 License

MIT License - Free for personal and educational use

## 👨‍💻 Author

**Neel Rana**
- GitHub: https://github.com/Neelrana12
- Email: neelrana126@gmail.com

---

**Last Updated**: April 2026
**Version**: 2.0 (Production Ready)

### Port 5000 already in use?
```bash
python -c "from app import app; app.run(port=5001)"
```

### Module not found?
```bash
pip install -r requirements.txt
```

### Can't login?
Check credentials:
- admin / password123
- user / user123

## 📧 Support

For deployment issues, check:
- Render dashboard: https://dashboard.render.com
- GitHub repository: https://github.com/Neelrana12/python_web

## 📄 License

This project is for Welltrade Surgipharma.

---

**Last Updated**: April 5, 2026  
**Version**: 1.0 (Fresh Start)  
**Status**: ✅ Live on corebuilds.me
