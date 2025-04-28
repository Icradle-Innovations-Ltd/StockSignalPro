from app import app
import os
from waitress import serve

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))

    if os.environ.get('FLASK_ENV') == 'production':
        print("🚀 Starting production server with Waitress...")
        serve(app, host=host, port=port, threads=8)
    else:
        print("🔧 Starting development server with Flask...")
        app.run(host=host, port=port, debug=True, threaded=True)
