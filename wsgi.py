from app import app
import os
from typing import Optional

# This is the WSGI entry point
application = app

if __name__ == '__main__':
    # Get port from environment variable with fallback to 5000
    port: int = int(os.getenv('PORT', '5000'))
    host: str = '0.0.0.0'

    # Check if we're in production
    if os.environ.get('FLASK_ENV') == 'production':
        try:
            from waitress import serve
            # Production server
            serve(app, host=host, port=port)
        except ImportError:
            print("Warning: Waitress not installed. Please install with: pip install waitress")
            exit(1)
    else:
        # Development server
        app.run(host=host, port=port, debug=True)