# Stock Market Signal Processing Web App - Installation Guide

This guide provides detailed instructions for setting up and deploying the Stock Market Signal Processing Web App in various environments.

## Prerequisites

Before starting installation, ensure you have the following prerequisites:

- Python 3.8 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)
- git (for cloning the repository)

## Local Development Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock-market-signal-processing.git
cd stock-market-signal-processing
```

### 2. Create a Virtual Environment

```bash
# On Linux/macOS
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

First, ensure PostgreSQL is installed and running. Then create a database:

```bash
# Access PostgreSQL
psql -U postgres

# In PostgreSQL shell
CREATE DATABASE stock_analysis;
CREATE USER stock_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stock_analysis TO stock_user;
\q
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://stock_user:your_password@localhost/stock_analysis
FLASK_SECRET_KEY=your_secure_random_key
FLASK_APP=main.py
FLASK_ENV=development
```

### 6. Initialize the Database

```bash
# With Flask initialized in your environment
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### 7. Run the Application

```bash
# Development server
flask run

# Or using Python directly
python main.py
```

The application should now be running at http://localhost:5000

## Production Deployment

### Option 1: Deploy with Gunicorn and Nginx

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Create a Gunicorn Configuration File

Create a file named `gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
timeout = 120
```

#### 3. Install and Configure Nginx

For Ubuntu/Debian:

```bash
sudo apt update
sudo apt install nginx
```

Create an Nginx site configuration:

```
# /etc/nginx/sites-available/stock-analysis
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/stock-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Set Up a Systemd Service

Create a file at `/etc/systemd/system/stock-analysis.service`:

```
[Unit]
Description=Stock Market Analysis Gunicorn Service
After=network.target

[Service]
User=yourusername
Group=yourusername
WorkingDirectory=/path/to/stock-market-signal-processing
Environment="PATH=/path/to/stock-market-signal-processing/venv/bin"
Environment="DATABASE_URL=postgresql://stock_user:your_password@localhost/stock_analysis"
Environment="FLASK_SECRET_KEY=your_secure_random_key"
ExecStart=/path/to/stock-market-signal-processing/venv/bin/gunicorn -c gunicorn_config.py main:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start stock-analysis
sudo systemctl enable stock-analysis
```

#### 5. Set Up SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Option 2: Deploy to a PaaS (Heroku)

#### 1. Install Heroku CLI

Follow the installation instructions at [Heroku Dev Center](https://devcenter.heroku.com/articles/heroku-cli).

#### 2. Login to Heroku

```bash
heroku login
```

#### 3. Create a Heroku App

```bash
heroku create your-app-name
```

#### 4. Provision a PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

#### 5. Set Environment Variables

```bash
heroku config:set FLASK_SECRET_KEY=your_secure_random_key
```

#### 6. Deploy the Application

```bash
git push heroku main
```

#### 7. Initialize the Database

```bash
heroku run python
```

In the Python shell:

```python
from app import db
db.create_all()
exit()
```

#### 8. Open the Application

```bash
heroku open
```

## Docker Deployment

### 1. Create a Dockerfile

Create a file named `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=main.py

EXPOSE 5000

CMD ["gunicorn", "--bind", "127.0.0.1:5000", "main:app"]
```

### 2. Create a docker-compose.yml File

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/stock_analysis
      - FLASK_SECRET_KEY=your_secure_random_key
    depends_on:
      - db
    restart: always

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=stock_analysis
    restart: always

volumes:
  postgres_data:
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up -d
```

The application should now be running at http://localhost:5000

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check connection strings and credentials
- Ensure the database user has proper permissions
- Check firewall settings if connecting to a remote database

### Package Installation Problems

- Upgrade pip: `pip install --upgrade pip`
- Install development packages if needed:
  
  ```bash
  # On Ubuntu/Debian
  sudo apt-get install python3-dev libpq-dev
  
  # On CentOS/RHEL
  sudo yum install python3-devel postgresql-devel
  ```

### Application Startup Issues

- Check log files:
  - Flask development server logs
  - Gunicorn logs: `/var/log/stock-analysis.log`
  - Nginx logs: `/var/log/nginx/error.log`
- Verify that the PostgreSQL database is accessible
- Ensure environment variables are correctly set

### Memory or Performance Issues

- Increase Gunicorn worker count for more traffic
- Optimize PostgreSQL settings for your server specs
- Consider adding a caching layer with Redis for high-traffic deployments

## System Requirements

### Minimum Requirements
- CPU: Dual-core processor
- RAM: 2GB
- Disk space: 1GB available
- Database: PostgreSQL 11+

### Recommended Requirements
- CPU: Quad-core processor
- RAM: 4GB
- Disk space: 5GB available
- Database: PostgreSQL 13+

## Security Recommendations

1. **Use HTTPS**: Always deploy with SSL in production
2. **Regular Updates**: Keep all dependencies updated
3. **Database Security**:
   - Use strong passwords
   - Limit database user permissions
   - Enable SSL for database connections
4. **Environment Variables**: Never commit sensitive information to version control
5. **Input Validation**: The application validates inputs, but maintain updates
6. **Backup Regularly**: Implement automated backups of your database