# Welltrade Surgipharma - Analytics Platform

A simple, clean Flask application for pharmaceutical company dashboard with login authentication and PowerBI integration ready.

## ✨ Features

- **Secure Login** - Username/password authentication
- **Dashboard** - Main welcome page with navigation
- **Sales Dashboard** - PowerBI placeholder (ready for integration)
- **Purchase Dashboard** - PowerBI placeholder (ready for integration)
- **Comparison Dashboard** - PowerBI placeholder (ready for integration)
- **Session Management** - Automatic logout after 24 hours
- **Responsive Design** - Works on all devices
- **Clean Code** - Beginner-friendly, easy to understand

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3
- **Authentication**: Flask Sessions
- **Deployment**: Render + Gunicorn
- **Domain**: corebuilds.me

## 📦 Requirements

```
Flask==3.0.0
Werkzeug==3.0.1
Jinja2==3.1.2
MarkupSafe==2.1.3
gunicorn==21.2.0
```

## 🚀 Quick Start (Local)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Open Browser
```
http://127.0.0.1:5000
```

### 4. Login
- **Username**: admin
- **Password**: password123

Alternatively:
- **Username**: user
- **Password**: user123

## 📁 Project Structure

```
python_web/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
├── runtime.txt              # Python version
├── templates/               # HTML templates
│   ├── login.html          # Login page
│   ├── base.html           # Base layout
│   ├── dashboard.html      # Main dashboard
│   ├── sales.html          # Sales dashboard (PowerBI ready)
│   ├── purchase.html       # Purchase dashboard (PowerBI ready)
│   └── comparison.html     # Comparison dashboard (PowerBI ready)
└── static/
    └── css/
        └── style.css       # Styling
```

## 🔐 Login Credentials

| Username | Password |
|----------|----------|
| admin | password123 |
| user | user123 |

## 📊 Dashboard Pages

1. **Dashboard** - Welcome page with links to all dashboards
2. **Sales** - Sales dashboard placeholder for PowerBI
3. **Purchase** - Purchase dashboard placeholder for PowerBI
4. **Comparison** - Sales vs Purchase comparison placeholder for PowerBI

## 🎨 Design

- **Color Scheme**: Purple gradient (#667eea, #764ba2)
- **Modern UI**: Clean, minimal design
- **Responsive**: Mobile-friendly layout
- **Professional**: Enterprise-ready styling

## 🌐 Live Deployment

- **URL**: https://corebuilds.me
- **Deployed on**: Render
- **Runtime**: Python 3.11.7 with Gunicorn

## 📝 API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page (redirects based on login status) |
| `/login` | GET, POST | Login page |
| `/logout` | GET | Logout (clear session) |
| `/dashboard` | GET | Main dashboard |
| `/sales` | GET | Sales dashboard |
| `/purchase` | GET | Purchase dashboard |
| `/comparison` | GET | Comparison dashboard |

## 🔒 Authentication

- Uses Flask sessions for authentication
- Session valid for 24 hours
- Secret key: `welltrade-secret-2024`
- Protected routes use `@login_required` decorator

## ⚙️ Configuration

- **Debug**: True (development)
- **Port**: 5000 (local) / Render (production)
- **Session Timeout**: 24 hours
- **Deployment**: Gunicorn (production server)

## 🚀 Next Steps

1. Add PowerBI dashboard links to:
   - `templates/sales.html`
   - `templates/purchase.html`
   - `templates/comparison.html`

2. Customize branding and colors as needed

3. Add database integration when needed

## 📚 Code Style

- **Language**: Python (Flask)
- **Simplicity**: Beginner-friendly code
- **Comments**: Well-commented for learning
- **Standards**: PEP 8 compliant

## 🐛 Troubleshooting

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
