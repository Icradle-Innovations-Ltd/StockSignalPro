from app import app
import os
from typing import Optional
from waitress import serve

# This is the WSGI entry point
application = app

if __name__ == '__main__':
    # Get port from environment variable with fallback to 5000
    port: int = int(os.getenv('PORT', '5000'))
    host: str = '127.0.0.1'

    # Check if we're in production
    if os.environ.get('FLASK_ENV') == 'production':
        # Production server using waitress
        serve(app, host=host, port=port)
    else:
        # Development server
        app.run(host=host, port=port, debug=True)