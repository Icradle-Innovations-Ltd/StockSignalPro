import os
import logging
import uuid
import io
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
import pandas as pd
import pdfkit
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

# Import utility modules
from utils.data_processing import process_data, perform_fft, detect_cycles
from utils.visualization import create_time_series_plot, create_frequency_plot, create_forecast_plot, convert_numpy_to_lists
from utils.decision_engine import generate_recommendation
from utils.api_fetcher import fetch_stock_data
from utils.sentiment_analysis import get_market_sentiment, create_sentiment_gauge
from utils.sample_data_generator import generate_sample_data_csv, get_sample_data_info, sample_ticker_symbol
from utils.portfolio_analysis import (create_portfolio, fetch_portfolio_data, calculate_correlation_matrix,
                                     create_correlation_heatmap, analyze_portfolio_cycles, 
                                     create_portfolio_cycle_chart, create_portfolio_performance_chart)

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
from models import db, Analysis, MarketSentiment, Portfolio
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

# Custom Jinja2 filters
@app.template_filter('datetime')
def format_datetime(value):
    """Format a datetime object to a readable string."""
    if isinstance(value, str):
        try:
            from dateutil import parser
            value = parser.parse(value)
        except (ValueError, ImportError):
            return value

    try:
        return value.strftime('%b %d, %Y at %I:%M %p')
    except:
        return value

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
                    dominant_cycles=convert_numpy_to_lists(dominant_cycles),
                    recommendation=convert_numpy_to_lists(recommendation),
                    time_series_plot=convert_numpy_to_lists(time_series_plot),
                    frequency_plot=convert_numpy_to_lists(frequency_plot),
                    forecast_plot=convert_numpy_to_lists(forecast_plot)
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
                dominant_cycles=convert_numpy_to_lists(dominant_cycles),
                recommendation=convert_numpy_to_lists(recommendation),
                time_series_plot=convert_numpy_to_lists(time_series_plot),
                frequency_plot=convert_numpy_to_lists(frequency_plot),
                forecast_plot=convert_numpy_to_lists(forecast_plot)
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
        html_report = render_template('report.html', analysis=analysis.to_dict(), now=now)

        pdf = pdfkit.from_string(html_report, False)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=analysis_report.pdf'
        return response


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

# Portfolio Analysis Routes
@app.route('/portfolios')
def portfolios():
    """Display all portfolios."""
    portfolios = Portfolio.query.order_by(Portfolio.updated_at.desc()).all()
    return render_template('portfolios/index.html', portfolios=portfolios)

@app.route('/portfolios/new', methods=['GET', 'POST'])
def create_portfolio():
    """Create a new portfolio."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        tickers_input = request.form.get('tickers', '').strip().upper()

        # Filter empty strings and strip whitespace
        tickers = [ticker.strip() for ticker in tickers_input.split(',') if ticker.strip()]

        # Handle allocations if provided
        allocations = {}
        if all(f'allocation_{ticker}' in request.form for ticker in tickers):
            for ticker in tickers:
                allocation_key = f'allocation_{ticker}'
                try:
                    allocation = float(request.form.get(allocation_key, 0))
                    allocations[ticker] = allocation
                except ValueError:
                    allocations[ticker] = 0

        # Validate
        if not name:
            flash('Portfolio name is required', 'danger')
            return render_template('portfolios/new.html')

        if not tickers:
            flash('At least one ticker is required', 'danger')
            return render_template('portfolios/new.html')

        try:
            # Log information for debugging
            logger.info(f"Creating portfolio with name: {name}, tickers: {tickers}")

            # Create default equal allocations if not provided
            if not allocations:
                allocation_pct = 100.0 / len(tickers)
                allocations = {ticker: allocation_pct for ticker in tickers}
            else:
                # Normalize allocations to 100%
                total = sum(allocations.values())
                if total > 0:
                    allocations = {ticker: (alloc / total * 100) for ticker, alloc in allocations.items()}

            # Create portfolio with minimal data first - we'll fetch the details later
            # This approach ensures we can at least create the portfolio structure
            portfolio = Portfolio(
                name=name,
                description=description,
                stocks=tickers,
                allocations=allocations
            )

            # Save to database
            db.session.add(portfolio)
            db.session.commit()

            # Now, try to fetch the data asynchronously (or at least log the attempt)
            logger.info(f"Portfolio created with ID: {portfolio.id} - Now fetching stock data")

            try:
                # Fetch data for the tickers (this will run, but we won't block portfolio creation on it)
                stock_data = fetch_portfolio_data(tickers, period="2y")

                if stock_data:
                    # If we got data, update the portfolio with analysis results
                    valid_tickers = list(stock_data.keys())

                    # Calculate correlation matrix
                    correlation_matrix = calculate_correlation_matrix(stock_data)

                    # Analyze cycles
                    cycle_analysis = analyze_portfolio_cycles(stock_data)

                    # Create portfolio performance chart
                    portfolio_chart = create_portfolio_performance_chart(stock_data, allocations)

                    # Update portfolio
                    portfolio.stocks = valid_tickers
                    portfolio.correlation_matrix = correlation_matrix.to_dict() if not correlation_matrix.empty else None
                    portfolio.cycle_analysis = cycle_analysis
                    portfolio.portfolio_plot = portfolio_chart

                    db.session.commit()
                    logger.info(f"Portfolio {portfolio.id} updated with analysis data")
                else:
                    logger.warning(f"Could not fetch stock data for portfolio {portfolio.id}")
            except Exception as data_error:
                # Don't fail the whole operation if just the data fetch fails
                logger.error(f"Error fetching data for portfolio {portfolio.id}: {str(data_error)}")

            flash('Portfolio created successfully', 'success')
            return redirect(url_for('view_portfolio', portfolio_id=portfolio.id))

        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            flash(f'Error creating portfolio: {str(e)}', 'danger')
            return render_template('portfolios/new.html')

    return render_template('portfolios/new.html')

@app.route('/portfolios/<portfolio_id>')
def view_portfolio(portfolio_id):
    """View a specific portfolio with analysis."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        flash('Portfolio not found', 'warning')
        return redirect(url_for('portfolios'))

    # Get all analyses associated with this portfolio
    analyses = Analysis.query.filter_by(portfolio_id=portfolio_id).all()

    # If portfolio has no analysis data yet, try to generate it now
    if portfolio.stocks and (portfolio.correlation_matrix is None or portfolio.cycle_analysis is None or portfolio.portfolio_plot is None):
        try:
            logger.info(f"Generating missing analysis data for portfolio {portfolio_id}")

            # Fetch data for the tickers
            stock_data = fetch_portfolio_data(portfolio.stocks, period="2y")

            if stock_data:
                # Calculate correlation matrix
                correlation_matrix = calculate_correlation_matrix(stock_data)

                # Analyze cycles
                cycle_analysis = analyze_portfolio_cycles(stock_data)

                # Create portfolio performance chart  
                portfolio_chart = create_portfolio_performance_chart(stock_data, portfolio.allocations)

                # Update portfolio
                if portfolio.correlation_matrix is None and not correlation_matrix.empty:
                    portfolio.correlation_matrix = correlation_matrix.to_dict()

                if portfolio.cycle_analysis is None:
                    portfolio.cycle_analysis = cycle_analysis

                if portfolio.portfolio_plot is None:
                    portfolio.portfolio_plot = portfolio_chart

                db.session.commit()
                logger.info(f"Portfolio {portfolio.id} updated with missing analysis data")
        except Exception as e:
            logger.error(f"Error generating analysis data for portfolio {portfolio_id}: {str(e)}")
            # Don't show this error to the user, just log it

    return render_template('portfolios/view.html', 
                          portfolio=portfolio.to_dict(), 
                          analyses=[a.to_dict() for a in analyses])

@app.route('/portfolios/<portfolio_id>/add_stock', methods=['POST'])
def add_stock_to_portfolio(portfolio_id):
    """Add a stock to an existing portfolio."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        flash('Portfolio not found', 'warning')
        return redirect(url_for('portfolios'))

    ticker = request.form.get('ticker', '').strip().upper()
    allocation = request.form.get('allocation', 0)

    try:
        allocation = float(allocation)
    except ValueError:
        allocation = 0

    if not ticker:
        flash('Ticker symbol is required', 'danger')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    # Check if ticker already exists in portfolio
    if ticker in portfolio.stocks:
        flash(f'{ticker} is already in this portfolio', 'warning')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    try:
        # Fetch data for the ticker
        df = fetch_stock_data(ticker, period="2y")

        if df.empty:
            flash(f'Could not fetch data for {ticker}', 'danger')
            return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

        # Add ticker to portfolio
        stocks = portfolio.stocks.copy() if portfolio.stocks else []
        stocks.append(ticker)

        # Update allocations
        allocations = portfolio.allocations.copy() if portfolio.allocations else {}
        allocations[ticker] = allocation

        # Update portfolio
        portfolio.stocks = stocks
        portfolio.allocations = allocations
        portfolio.updated_at = datetime.utcnow()

        # Refetch all portfolio data and recalculate metrics
        stock_data = fetch_portfolio_data(stocks, period="2y")

        # Update correlation matrix
        correlation_matrix = calculate_correlation_matrix(stock_data)
        portfolio.correlation_matrix = correlation_matrix.to_dict() if not correlation_matrix.empty else None

        # Update cycle analysis
        cycle_analysis = analyze_portfolio_cycles(stock_data)
        portfolio.cycle_analysis = cycle_analysis

        # Update portfolio chart
        portfolio_chart = create_portfolio_performance_chart(stock_data, allocations)
        portfolio.portfolio_plot = portfolio_chart

        # Save to database
        db.session.commit()

        flash(f'{ticker} added to portfolio successfully', 'success')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    except Exception as e:
        logger.error(f"Error adding stock to portfolio: {str(e)}")
        flash(f'Error adding stock to portfolio: {str(e)}', 'danger')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

@app.route('/portfolios/<portfolio_id>/remove_stock/<ticker>', methods=['POST'])
def remove_stock_from_portfolio(portfolio_id, ticker):
    """Remove a stock from a portfolio."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        flash('Portfolio not found', 'warning')
        return redirect(url_for('portfolios'))

    if not ticker or ticker not in portfolio.stocks:
        flash('Stock not found in portfolio', 'warning')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    try:
        # Remove ticker from portfolio
        stocks = [t for t in portfolio.stocks if t != ticker]

        # Update allocations
        allocations = {t: a for t, a in portfolio.allocations.items() if t != ticker}

        # Update portfolio
        portfolio.stocks = stocks
        portfolio.allocations = allocations
        portfolio.updated_at = datetime.utcnow()

        # If portfolio is now empty, handle gracefully
        if not stocks:
            portfolio.correlation_matrix = None
            portfolio.cycle_analysis = None
            portfolio.portfolio_plot = None

            # Save to database
            db.session.commit()

            flash(f'{ticker} removed from portfolio', 'success')
            return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

        # Refetch all portfolio data and recalculate metrics
        stock_data = fetch_portfolio_data(stocks, period="2y")

        # Update correlation matrix
        correlation_matrix = calculate_correlation_matrix(stock_data)
        portfolio.correlation_matrix = correlation_matrix.to_dict() if not correlation_matrix.empty else None

        # Update cycle analysis
        cycle_analysis = analyze_portfolio_cycles(stock_data)
        portfolio.cycle_analysis = cycle_analysis

        # Update portfolio chart
        portfolio_chart = create_portfolio_performance_chart(stock_data, allocations)
        portfolio.portfolio_plot = portfolio_chart

        # Save to database
        db.session.commit()

        flash(f'{ticker} removed from portfolio', 'success')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    except Exception as e:
        logger.error(f"Error removing stock from portfolio: {str(e)}")
        flash(f'Error removing stock from portfolio: {str(e)}', 'danger')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

@app.route('/portfolios/<portfolio_id>/update_allocations', methods=['POST'])
def update_portfolio_allocations(portfolio_id):
    """Update allocation percentages for a portfolio."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        flash('Portfolio not found', 'warning')
        return redirect(url_for('portfolios'))

    try:
        # Get allocations from form
        allocations = {}
        for ticker in portfolio.stocks:
            allocation_key = f'allocation_{ticker}'
            try:
                allocation = float(request.form.get(allocation_key, 0))
                allocations[ticker] = allocation
            except ValueError:
                allocations[ticker] = 0

        # Normalize to 100%
        total = sum(allocations.values())
        if total > 0:
            allocations = {ticker: (alloc / total * 100) for ticker, alloc in allocations.items()}

        # Update portfolio
        portfolio.allocations = allocations
        portfolio.updated_at = datetime.utcnow()

        # Refetch portfolio data
        stock_data = fetch_portfolio_data(portfolio.stocks, period="2y")

        # Update portfolio chart with new allocations
        portfolio_chart = create_portfolio_performance_chart(stock_data, allocations)
        portfolio.portfolio_plot = portfolio_chart

        # Save to database
        db.session.commit()

        flash('Portfolio allocations updated successfully', 'success')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

    except Exception as e:
        logger.error(f"Error updating portfolio allocations: {str(e)}")
        flash(f'Error updating portfolio allocations: {str(e)}', 'danger')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

@app.route('/portfolios/<portfolio_id>/delete', methods=['POST'])
def delete_portfolio(portfolio_id):
    """Delete a portfolio."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        flash('Portfolio not found', 'warning')
        return redirect(url_for('portfolios'))

    try:
        # Remove portfolio
        db.session.delete(portfolio)
        db.session.commit()

        flash('Portfolio deleted successfully', 'success')
        return redirect(url_for('portfolios'))

    except Exception as e:
        logger.error(f"Error deleting portfolio: {str(e)}")
        flash(f'Error deleting portfolio: {str(e)}', 'danger')
        return redirect(url_for('view_portfolio', portfolio_id=portfolio_id))

@app.route('/api/portfolio_plots/<portfolio_id>/<plot_type>')
def get_portfolio_plot(portfolio_id, plot_type):
    """API endpoint to get portfolio plot data."""
    portfolio = Portfolio.query.get(portfolio_id)

    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404

    try:
        if plot_type == 'performance' and portfolio.portfolio_plot:
            return jsonify(portfolio.portfolio_plot)
        elif plot_type == 'correlation' and portfolio.correlation_matrix:
            # Create correlation heatmap from stored matrix
            import pandas as pd
            matrix_dict = portfolio.correlation_matrix
            correlation_df = pd.DataFrame(matrix_dict)
            heatmap = create_correlation_heatmap(correlation_df)
            return jsonify(heatmap)
        elif plot_type == 'cycles' and portfolio.cycle_analysis:
            # Fetch stock data and recreate cycle chart
            stock_data = fetch_portfolio_data(portfolio.stocks, period="2y")
            cycle_chart = create_portfolio_cycle_chart(portfolio.cycle_analysis, stock_data)
            return jsonify(cycle_chart)
        else:
            return jsonify({'error': 'Invalid plot type or plot not found'}), 400

    except Exception as e:
        logger.error(f"Error retrieving portfolio plot: {str(e)}")
        return jsonify({'error': f'Error retrieving plot: {str(e)}'}), 500

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

@app.route('/market-sentiment', methods=['GET'])
def market_sentiment_page():
    """Display the market sentiment page with mood indicator."""
    # Check if we have recent sentiment data
    recent_sentiment = MarketSentiment.query.order_by(MarketSentiment.created_at.desc()).first()

    # If no recent sentiment or older than 1 hour, fetch new
    if not recent_sentiment or (datetime.utcnow() - recent_sentiment.created_at).total_seconds() > 3600:
        try:
            # Get market sentiment
            sentiment_data = get_market_sentiment()

            # Create gauge chart
            sentiment_gauge = create_sentiment_gauge(sentiment_data)

            # Create new sentiment record
            sentiment = MarketSentiment(
                bullish_score=sentiment_data['bullish_score'],
                bearish_score=sentiment_data['bearish_score'],
                neutral_score=sentiment_data['neutral_score'],
                mood=sentiment_data['mood'],
                mood_value=sentiment_data['mood_value'],
                sentiment_gauge=convert_numpy_to_lists(sentiment_gauge)
            )

            # Save to database
            db.session.add(sentiment)
            db.session.commit()

            return render_template('market_sentiment.html', sentiment=sentiment.to_dict())
        except Exception as e:
            logger.error(f"Error fetching market sentiment: {str(e)}")
            flash(f'Error fetching market sentiment: {str(e)}', 'danger')
            return redirect(url_for('index'))

    # Use recent sentiment data
    return render_template('market_sentiment.html', sentiment=recent_sentiment.to_dict())

@app.route('/system-report')
def system_report():
    """Display the system report page."""
    return render_template('system_report.html', now=datetime.now)

@app.route('/api/market-sentiment', methods=['GET'])
def get_market_sentiment_api():
    """API endpoint to get market sentiment data."""
    ticker = request.args.get('ticker')

    try:
        # Get market sentiment data
        sentiment_data = get_market_sentiment(ticker=ticker)

        # Create gauge chart
        sentiment_gauge = create_sentiment_gauge(sentiment_data)

        # Create response
        response = {
            'sentiment': sentiment_data,
            'gauge_chart': convert_numpy_to_lists(sentiment_gauge)
        }

        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting market sentiment: {str(e)}")
        return jsonify({'error': f'Error getting market sentiment: {str(e)}'}), 500

@app.route('/ticker-sentiment/<ticker>')
def ticker_sentiment(ticker):
    """Display sentiment analysis for a specific ticker."""
    try:
        # Get sentiment for specific ticker
        sentiment_data = get_market_sentiment(ticker=ticker)

        # Create gauge chart
        sentiment_gauge = create_sentiment_gauge(sentiment_data)

        # Create new sentiment record
        sentiment = MarketSentiment(
            ticker=ticker,
            bullish_score=sentiment_data['bullish_score'],
            bearish_score=sentiment_data['bearish_score'],
            neutral_score=sentiment_data['neutral_score'],
            mood=sentiment_data['mood'],
            mood_value=sentiment_data['mood_value'],
            sentiment_gauge=convert_numpy_to_lists(sentiment_gauge)
        )

        # Save to database
        db.session.add(sentiment)
        db.session.commit()

        return render_template('ticker_sentiment.html', sentiment=sentiment.to_dict(), ticker=ticker)
    except Exception as e:
        logger.error(f"Error fetching sentiment for {ticker}: {str(e)}")
        flash(f'Error fetching sentiment for {ticker}: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/sample-data')
def sample_data_page():
    """Display the sample data generation page."""
    # Get sample data info
    sample_data_info = get_sample_data_info()
    return render_template('sample_data.html', sample_data_info=sample_data_info)

@app.route('/api/sample-data/<stock_type>', methods=['GET'])
def generate_sample_data(stock_type):
    """Generate and return sample stock data as CSV."""
    try:
        # Get optional parameters from request
        params = {}
        if 'days' in request.args:
            params['days'] = int(request.args.get('days'))
        if 'start_price' in request.args:
            params['start_price'] = float(request.args.get('start_price'))

        # Generate the sample data CSV
        csv_data = generate_sample_data_csv(stock_type=stock_type, params=params)

        # Generate random ticker for filename
        ticker = sample_ticker_symbol()

        # Return as downloadable file
        return send_file(
            io.BytesIO(csv_data.encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{ticker}_sample_data.csv"
        )
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        return jsonify({'error': f'Error generating sample data: {str(e)}'}), 500

@app.errorhandler(500)
def server_error(e):
    return render_template('index.html', error="Server error occurred"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)