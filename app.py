import os
import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import pandas as pd
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import io

# Import utility modules
from utils.data_processing import process_data, perform_fft, detect_cycles
from utils.visualization import create_time_series_plot, create_frequency_plot, create_forecast_plot
from utils.decision_engine import generate_recommendation
from utils.api_fetcher import fetch_stock_data

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Import and initialize the database
from models import db, Analysis
db.init_app(app)

with app.app_context():
    db.create_all()

# Configure uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page with upload form and ticker search."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload or ticker symbol entry."""
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Read the CSV directly
                df = pd.read_csv(file)
                
                # Basic validation
                if 'date' not in df.columns and 'Date' not in df.columns:
                    flash('CSV must contain a date/Date column', 'danger')
                    return redirect(url_for('index'))
                
                # Check for price column
                price_columns = [col for col in df.columns if 'price' in col.lower() or 'close' in col.lower()]
                if not price_columns:
                    flash('CSV must contain price/close data', 'danger')
                    return redirect(url_for('index'))
                
                # Process the data
                df = process_data(df)
                fft_results = perform_fft(df)
                dominant_cycles = detect_cycles(fft_results)
                
                # Generate recommendation
                recommendation = generate_recommendation(df, dominant_cycles)
                
                # Create plots
                time_series_plot = create_time_series_plot(df)
                frequency_plot = create_frequency_plot(fft_results)
                forecast_plot = create_forecast_plot(df, dominant_cycles)
                
                # Create a new analysis record in the database
                analysis = Analysis(
                    source_type='file',
                    filename=secure_filename(file.filename),
                    dominant_cycles=dominant_cycles,
                    recommendation=recommendation,
                    time_series_plot=time_series_plot,
                    frequency_plot=frequency_plot,
                    forecast_plot=forecast_plot
                )
                
                # Save to database
                db.session.add(analysis)
                db.session.commit()
                
                # Redirect to results page
                return redirect(url_for('results', analysis_id=analysis.id))
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                flash(f'Error processing file: {str(e)}', 'danger')
                return redirect(url_for('index'))
        else:
            flash('Only CSV files are allowed', 'warning')
            return redirect(url_for('index'))
    
    # Handle ticker symbol input
    elif 'ticker' in request.form and request.form['ticker']:
        ticker = request.form['ticker'].strip().upper()
        try:
            # Fetch data for the ticker
            df = fetch_stock_data(ticker)
            
            # Process the data
            df = process_data(df)
            fft_results = perform_fft(df)
            dominant_cycles = detect_cycles(fft_results)
            
            # Generate recommendation
            recommendation = generate_recommendation(df, dominant_cycles)
            
            # Create plots
            time_series_plot = create_time_series_plot(df)
            frequency_plot = create_frequency_plot(fft_results)
            forecast_plot = create_forecast_plot(df, dominant_cycles)
            
            # Create a new analysis record in the database
            analysis = Analysis(
                source_type='api',
                ticker=ticker,
                dominant_cycles=dominant_cycles,
                recommendation=recommendation,
                time_series_plot=time_series_plot,
                frequency_plot=frequency_plot,
                forecast_plot=forecast_plot
            )
            
            # Save to database
            db.session.add(analysis)
            db.session.commit()
            
            # Redirect to results page
            return redirect(url_for('results', analysis_id=analysis.id))
            
        except Exception as e:
            logger.error(f"Error fetching ticker data: {str(e)}")
            flash(f'Error fetching data for {ticker}: {str(e)}', 'danger')
            return redirect(url_for('index'))
    
    flash('Please provide a file or ticker symbol', 'warning')
    return redirect(url_for('index'))

@app.route('/results/<analysis_id>')
def results(analysis_id):
    """Display analysis results."""
    # Get analysis from database
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        flash('Analysis not found or expired', 'warning')
        return redirect(url_for('index'))
    
    return render_template('results.html', analysis=analysis.to_dict())

@app.route('/api/plots/<analysis_id>/<plot_type>', methods=['GET'])
def get_plot(analysis_id, plot_type):
    """API endpoint to get plot data."""
    # Debug log to track API requests
    print(f"DEBUG: API request received for plot. Analysis ID: {analysis_id}, Plot Type: {plot_type}")
    
    # Get analysis from database
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        print(f"DEBUG: Analysis not found with ID: {analysis_id}")
        return jsonify({'error': 'Analysis not found or expired'}), 404
    
    try:
        print(f"DEBUG: Analysis found, checking for plot data. Has time_series_plot: {analysis.time_series_plot is not None}")
        print(f"DEBUG: Has frequency_plot: {analysis.frequency_plot is not None}")
        print(f"DEBUG: Has forecast_plot: {analysis.forecast_plot is not None}")
        
        # Return the stored plot data directly
        if plot_type == 'time_series' and analysis.time_series_plot:
            print("DEBUG: Returning time_series_plot data")
            return jsonify(analysis.time_series_plot)
        elif plot_type == 'frequency' and analysis.frequency_plot:
            print("DEBUG: Returning frequency_plot data")
            return jsonify(analysis.frequency_plot)
        elif plot_type == 'forecast' and analysis.forecast_plot:
            print("DEBUG: Returning forecast_plot data")
            return jsonify(analysis.forecast_plot)
        else:
            print(f"DEBUG: Invalid plot type or plot not found: {plot_type}")
            return jsonify({'error': 'Invalid plot type or plot not found'}), 400
    
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        logger.error(f"Error retrieving plot: {str(e)}")
        return jsonify({'error': f'Error retrieving plot: {str(e)}'}), 500

@app.route('/generate_report/<analysis_id>')
def generate_report(analysis_id):
    """Generate and download a PDF report of the analysis."""
    # Get analysis from database
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        flash('Analysis not found or expired', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Add a helper function for the template to format dates
        def now():
            from datetime import datetime
            return datetime.now()
            
        # In a real implementation, this would generate a PDF
        # For now, we'll render an HTML report that could be printed
        return render_template('report.html', analysis=analysis.to_dict(), now=now)
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('results', analysis_id=analysis_id))

@app.route('/download_csv/<analysis_id>')
def download_csv(analysis_id):
    """Download analysis results as CSV."""
    # Get analysis from database
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        flash('Analysis not found or expired', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Create a DataFrame with the results
        # In a real implementation, we'd have more complete data
        data = {
            'Cycle Length (Days)': [cycle['length'] for cycle in analysis.dominant_cycles],
            'Cycle Strength': [cycle['strength'] for cycle in analysis.dominant_cycles],
            'Current Phase': [cycle['phase'] for cycle in analysis.dominant_cycles]
        }
        
        results_df = pd.DataFrame(data)
        
        # Create a string buffer
        buffer = io.StringIO()
        results_df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        # Create a unique filename
        if analysis.ticker:
            filename = f"{analysis.ticker}_cycle_analysis.csv"
        else:
            filename = f"{analysis.filename.split('.')[0]}_cycle_analysis.csv"
        
        # Return the CSV as a downloadable file
        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"Error downloading CSV: {str(e)}")
        flash(f'Error downloading CSV: {str(e)}', 'danger')
        return redirect(url_for('results', analysis_id=analysis_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found"), 404

# Feature and Resource Pages
@app.route('/features/cycle-detection')
def cycle_detection():
    return render_template('features/cycle_detection.html')

@app.route('/features/fft-analysis')
def fft_analysis():
    return render_template('features/fft_analysis.html')

@app.route('/features/trading-signals')
def trading_signals():
    return render_template('features/trading_signals.html')

@app.route('/features/stock-forecasting')
def stock_forecasting():
    return render_template('features/stock_forecasting.html')

@app.route('/resources/documentation')
def documentation():
    return render_template('resources/documentation.html')

@app.route('/resources/api')
def api_docs():
    return render_template('resources/api.html')

@app.route('/resources/blog')
def blog():
    return render_template('resources/blog.html')

@app.route('/resources/support')
def support():
    return render_template('resources/support.html')

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Server error occurred"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
