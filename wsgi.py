from app import app
import os
from typing import Optional
from waitress import serve

# This is the WSGI entry point
application = app

if __name__ == '__main__':
    # Get port from environment variable with fallback to 5000
    port: int = int(os.getenv('PORT', '5000'))
    host: str = '0.0.0.0'

    import os
from app import app
from waitress import serve

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    
    if os.environ.get('FLASK_ENV') == 'production':
        # Production server using Waitress
        print("Starting production server with Waitress...")
        serve(app, host=host, port=port, threads=8)
    else:
        # Development server
        print("Starting development server with Flask...")
        app.run(host=host, port=port, debug=True, threaded=True)
