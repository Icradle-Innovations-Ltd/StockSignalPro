Alright — you're doing very well moving between dev and production!  
Let's **summarize** and **properly update your README** now, *including everything*, clear for **both Development and Production setup**.

Here’s your complete updated README.md:

---

# 📈 StockSignalPro

A Flask-based application for stock analysis, signal generation, and portfolio management.

---

## 🚀 Features
- Upload your portfolio and analyze stock signals
- Time series forecasting
- Market sentiment visualization
- Export analysis to PDF
- Production-ready (Waitress server)
- Development-ready (Flask server)

---

## 🛠 Installation

### 1. Clone the repo
```bash
git clone https://your-repo-url.git
cd StockSignalPro
```

### 2. Create and activate a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python13 -m venv .venv
source .venv/bin/activate```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📜 Environment Variables

Create a `.env` file with:

```env
FLASK_ENV=development
PORT=5000
```

> - For production set `FLASK_ENV=production`
> - Default port is 5000

---

## 🧪 Running in Development Mode

```bash
python wsgi.py
```
# Then set environment variable and run:
set FLASK_ENV=development && python wsgi.py

- App available at: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Flask built-in server used with `debug=True`.
- Auto-reloads on code changes.

---

## 🏭 Running in Production Mode

1. **Set the environment** (on Windows):for cmd
   ```bash
   .venv\Scripts\activate
set FLASK_ENV=production && python wsgi.py

# For Bash
source .venv/Scripts/activate
set FLASK_ENV=production && python wsgi.py
# Terminal | How to Activate Venv
# CMD 
.venv\Scripts\activate.bat
# PowerShell 
.venv\Scripts\Activate.ps1
# Git Bash 
source .venv/Scripts/activate
   ```

2. **Run the app**:
   ```bash
   python wsgi.py
   ```
# To make sure it runs in production mode, you need to set the FLASK_ENV environment variable to production.
source .venv/Scripts/activate
export FLASK_ENV=production
python wsgi.py
- App available at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

- **Waitress server** starts listening on all interfaces (`0.0.0.0:5000`).
- Suitable for production.
- No automatic reload.

---

## ⚡ Important: `wkhtmltopdf`

PDF generation requires **wkhtmltopdf** installed!

- Install it from: https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf
- Then make sure it's accessible via PATH.

**Windows Quick Install**:
```bash
choco install wkhtmltopdf
```

Otherwise you will see warnings like:
> No wkhtmltopdf executable found: "/usr/bin/wkhtmltopdf"

---

## 📦 Freeze Environment (for lock files)

To generate exact package versions (for deployment):

```bash
pip freeze > requirements.lock
```

Then you can reinstall exactly later with:
```bash
pip install -r requirements.lock
```

---

## 📄 Project Structure

```bash
StockSignalPro/
│
├── app.py             # Flask main app
├── wsgi.py            # Production-ready entry point
├── models.py          # Database models
├── utils/             # Helper functions
├── static/            # CSS, JS, images
├── templates/         # HTML pages
├── .env               # Environment settings
├── requirements.txt   # Main dependencies
├── requirements.lock  # Exact versions
└── README.md          # This file
```

---

## 🛠 Debugging Issues
- Set `FLASK_ENV=development` to get verbose error logs
- Use browser console (`F12`) for frontend errors
- If you get **ERR_ADDRESS_INVALID** make sure you connect to:
  - [http://127.0.0.1:5000](http://127.0.0.1:5000) for local testing
- If you get **SSL/TLS errors** you may have tried HTTPS by mistake — use HTTP for local development.
- For `wkhtmltopdf` missing — install it manually and verify it's on PATH.

---

# 📢 Notes

- This app **is NOT secure out of the box**. For a full production system, add:
  - HTTPS (via Nginx, Caddy, etc.)
  - Gunicorn with Nginx proxy
  - Docker containerization
- Use `flask-talisman` to enforce HTTPS and security headers in production.

---

# 🧑‍💻 Author
**ULTIMATE INVESTOR TEAM**

---

# ✅ Quick Commands Cheat Sheet

| Action | Command |
|:---|:---|
| Install all deps | `pip install -r requirements.txt` |
| Freeze env | `pip freeze > requirements.lock` |
| Run dev server | `python wsgi.py` |
| Set production | `set FLASK_ENV=production && python wsgi.py` |

---

# 🎯 You are now 100% Production + Development Ready.

---
