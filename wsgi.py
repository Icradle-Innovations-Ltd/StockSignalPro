import os
from app import app
from waitress import serve

application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    host = '127.0.0.1'

    if os.getenv('FLASK_ENV') == 'production':
        print("🚀 Starting production server with Waitress...")
        serve(app, host=host, port=port, threads=8)
    else:
        print("🔧 Starting development server with Flask...")
        app.run(host=host, port=port, debug=True, threaded=True)
