import os
from app import app
from waitress import serve
from dotenv import load_dotenv

load_dotenv()

application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))

    if os.getenv('FLASK_ENV') == 'production':
        host = '0.0.0.0'
        print(f"🚀 Starting production server at {host}:{port}...")
        serve(app, host=host, port=port, threads=8)
    else:
        host = '127.0.0.1'
        print(f"🔧 Starting development server at {host}:{port}...")
        app.run(host=host, port=port, debug=True, threaded=True)