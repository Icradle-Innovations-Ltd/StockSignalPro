from app import app  # noqa: F401
import os

if __name__ == "__main__":
    # Get port from environment variables, fallback to 5000
    port = int(os.getenv('PORT', 5000))
    host = '127.0.0.1'

    print("🛠️ Starting development server with Flask...")
    app.run(host=host, port=port, debug=True, threaded=True)
