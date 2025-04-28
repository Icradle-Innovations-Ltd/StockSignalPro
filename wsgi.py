import os
from app import app
from waitress import serve
from dotenv import load_dotenv

load_dotenv()  # ✅ Load environment variables from a .env file (great for dev)

application = app  # ✅ For Gunicorn to find when it runs wsgi:application

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))  # ✅ Dynamically pick port (Render injects $PORT)

    if os.getenv('FLASK_ENV') == 'production':
        host = '0.0.0.0'  # ✅ Bind externally for cloud deployment
        print(f"🚀 Starting production server at {host}:{port}...")
        serve(app, host=host, port=port, threads=8)  # ✅ Waitress is production-ready WSGI server
    else:
        host = '127.0.0.1'  # ✅ Local development only
        print(f"🔧 Starting development server at {host}:{port}...")
        app.run(host=host, port=port, debug=True, threaded=True)  # ✅ Built-in Flask server for dev
