Got it — you want a full **README** including **all debugging steps and warnings** like:

- `wkhtmltopdf` missing
- common port issues
- network errors (`ERR_SSL_PROTOCOL_ERROR`)
- how to fix `gunicorn` on Windows
- how to switch to Waitress
- and localhost access issues

I'll **rebuild** the README fully now, **step-by-step** and **proper**.

---

# 📄 StockSignalPro - Complete Local Setup & Debugging Guide

## 1. Environment Setup

```bash
# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Running the Application

```bash
python main.py
```
- **Default**: runs at [http://127.0.0.1:5000](http://127.0.0.1:5000)
- If you get port conflicts, change the port via `PORT` environment variable.

---

## 3. Debugging Common Problems

### 🔥 Problem: `wkhtmltopdf not found`
- **Warning Message**:
  > PDF generation may not work: No wkhtmltopdf executable found...

- **Solution**:
  1. Download `wkhtmltopdf` here: [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
  2. Install it and **add to your system PATH**.
  3. Restart your terminal / IDE.

---

### 🔥 Problem: `ERR_SSL_PROTOCOL_ERROR` or `Bad Request`
- **Cause**: You're accessing **http://** via a browser trying to force **https://**.
- **Solution**:
  1. Open: [http://127.0.0.1:5000](http://127.0.0.1:5000) manually.
  2. Do not add **https** unless you configured SSL certificates.

---

### 🔥 Problem: `gunicorn` not working on Windows
- **Error**:  
  > ModuleNotFoundError: No module named 'fcntl'

- **Cause**: Gunicorn is Linux only.
- **Solution**: Use **Waitress** instead.

```python
# Inside main.py
if __name__ == "__main__":
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)
```

Or run manually:

```bash
pip install waitress
python main.py
```

---

### 🔥 Problem: `localhost not loading`
- Check your firewall / antivirus settings.
- Ensure your app binds to `127.0.0.1` not `0.0.0.0` if you only want local access.
- Check you are NOT accessing via HTTPS if server is HTTP-only.

---

## 4. Production Notes

- Use **Waitress** for production on Windows.
- Use **Gunicorn** for production on Linux/Unix.
- Always set `FLASK_ENV=production` in production environment.

```bash
set FLASK_ENV=production  # Windows
export FLASK_ENV=production  # macOS/Linux
```

---

## 5. Example Usage Commands

```bash
# Activate environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server in development mode
python main.py

# (Optional) Run server with Waitress
python -m waitress main:app
```

---

## 6. Useful Resources

- [wkhtmltopdf Installation Help](https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf)
- [Flask Official Documentation](https://flask.palletsprojects.com/)
- [Waitress WSGI Server](https://docs.pylonsproject.org/projects/waitress/en/stable/)

---

# ✅ Final Reminder
**Don't run Flask built-in server in production.**  
Always switch to a proper WSGI server like **Waitress** or **Gunicorn**!

---

### Would you also want me to create a ready downloadable `README.md` file version you can save directly? 🚀
(If yes, I'll generate it immediately.)