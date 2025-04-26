
from app import app
import os

if __name__ == '__main__':
    # Check if we're in production
    if os.environ.get('FLASK_ENV') == 'production':
        from waitress import serve
        # Production server
        serve(app, host='0.0.0.0', port=5000)
    else:
        # Development server
        app.run(host='0.0.0.0', port=5000, debug=True)
