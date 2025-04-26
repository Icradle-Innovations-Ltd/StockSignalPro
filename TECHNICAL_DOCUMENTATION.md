# Stock Market Signal Processing Web App - Technical Documentation

This document provides detailed technical information about the Stock Market Signal Processing Web App, including architecture, data processing algorithms, and implementation details.

## Architecture Overview

The application follows a Model-View-Controller (MVC) architecture with Flask as the web framework:

- **Model**: Defined in `models.py` using SQLAlchemy ORM with PostgreSQL database
- **View**: Implemented as Jinja2 templates in the `templates/` directory
- **Controller**: Implemented in `app.py` as Flask routes

### Component Diagram
```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Web Browser  │◄────┤ Flask Routes  │◄────┤ Data Models   │
│  (User)       │     │ (Controller)  │     │ (Model)       │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │                     ▼                     │
        │             ┌───────────────┐             │
        └────────────┤ Jinja2        │◄────────────┘
                     │ Templates     │
                     │ (View)        │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Utilities     │
                     │ (Processing)  │
                     └───────────────┘
                         ┌─────┴─────┐
           ┌─────────────┴───┐   ┌───┴─────────────┐
┌──────────▼───────────┐ ┌───▼───────────────┐ ┌───▼───────────────┐
│ API Fetcher          │ │ Data Processing   │ │ Visualization     │
│ (Stock Data)         │ │ (FFT Analysis)    │ │ (Plotly Graphs)   │
└──────────────────────┘ └───────────────────┘ └───────────────────┘
```

## Database Schema

The application uses a PostgreSQL database with the following schema:

### Analysis Table
- **id** (UUID, Primary Key): Unique identifier for analysis sessions
- **ticker** (String): Stock ticker symbol
- **created_at** (DateTime): Timestamp of analysis
- **source_type** (String): Data source type ("file" or "api")
- **filename** (String): Name of uploaded file (if applicable)
- **data** (JSON): Processed stock data
- **recommendation** (JSON): Trading recommendation
- **dominant_cycles** (JSON): Detected cycles information
- **time_series_plot** (JSON): Time series plot data
- **frequency_plot** (JSON): Frequency domain plot data
- **forecast_plot** (JSON): Forecast plot data

### MarketSentiment Table
- **id** (UUID, Primary Key): Unique identifier for sentiment analysis
- **ticker** (String, Nullable): Optional ticker symbol for stock-specific sentiment
- **created_at** (DateTime): Timestamp of sentiment analysis
- **bullish_score** (Float): Percentage of bullish indicators (0-100)
- **bearish_score** (Float): Percentage of bearish indicators (0-100)
- **neutral_score** (Float): Percentage of neutral indicators (0-100)
- **mood** (String): Overall sentiment classification ("bullish", "bearish", or "neutral")
- **mood_value** (Float): Numeric value representing sentiment (0-100)
- **sentiment_gauge** (JSON): Plotly chart JSON for sentiment gauge visualization

## Data Processing Pipeline

### 1. Data Acquisition
- **CSV Upload**: Processes uploaded CSV files with date and price columns
- **API Fetcher**: Fetches stock data from Yahoo Finance API using ticker symbol and period

### 2. Data Preprocessing (`utils/data_processing.py`)
- **Cleaning**: Handles missing values and outliers
- **Normalization**: Scales price data for more consistent analysis
- **Detrending**: Removes long-term trends to focus on cyclic behavior
- **Date Conversion**: Converts date strings to numerical index for FFT analysis

### 3. FFT Analysis (`utils/data_processing.py`)
```python
def perform_fft(df):
    """
    1. Extract price data
    2. Apply windowing function to reduce spectral leakage
    3. Compute FFT using scipy.fft
    4. Calculate frequencies, periods, amplitudes, and phases
    5. Return results as dictionary
    """
    
def detect_cycles(fft_results, min_period=2, max_period=252, strength_threshold=0.1):
    """
    1. Filter periods between min_period and max_period
    2. Sort by amplitude to find strongest cycles
    3. Calculate relative strength as percentage of total signal power
    4. Filter by strength_threshold
    5. Return list of cycles with period, amplitude, phase, and strength
    """
```

### 4. Decision Engine (`utils/decision_engine.py`)
- **Recommendation Generation**: Analyzes cycle positions to generate Buy/Hold/Sell advice
- **Confidence Calculation**: Determines confidence level based on cycle clarity and strength
- **Reasoning**: Provides contextual explanation for the recommendation

### 5. Visualization Creation (`utils/visualization.py`)
- **Time Series Plot**: Shows historical prices with moving averages
- **Frequency Plot**: Displays power spectrum with dominant cycles highlighted
- **Forecast Plot**: Projects future prices based on cycle superposition
- **Sentiment Gauge**: Visualizes market sentiment on a 0-100 scale

### 6. Sentiment Analysis (`utils/sentiment_analysis.py` & `utils/web_scraper.py`)
- **Web Scraping**: Extracts text content from financial news sources
- **Text Analysis**: Identifies bullish, bearish, and neutral keywords and phrases
- **Sentiment Scoring**: Calculates sentiment scores based on keyword frequency and weight
- **Gauge Visualization**: Creates interactive gauge chart to display sentiment visually

## Algorithm Details

### Fast Fourier Transform (FFT)
The FFT algorithm transforms time-domain data into the frequency domain, revealing periodic patterns:

1. The discrete Fourier transform of a price signal is computed:
   ```
   X(k) = Σ[n=0 to N-1] x(n) * e^(-j2πkn/N)
   ```
   Where:
   - `x(n)` is the price data
   - `N` is the number of data points
   - `k` is the frequency index

2. The amplitude at each frequency is calculated as:
   ```
   |X(k)| = sqrt(real(X(k))^2 + imag(X(k))^2)
   ```

3. The phase at each frequency is calculated as:
   ```
   φ(k) = atan2(imag(X(k)), real(X(k)))
   ```

4. Frequencies are converted to periods (in days) for easier interpretation:
   ```
   period = N / k
   ```

### Cycle Detection
Dominant cycles are identified through peak detection in the frequency domain:

1. Local maxima in the amplitude spectrum represent potential cycles
2. Peaks are ranked by amplitude and filtered by minimum strength threshold
3. Period ranges are constrained to meaningful market cycles (2-252 days)
4. Phase calculation determines the current position within each cycle

### Trading Recommendation Logic
Buy/Hold/Sell recommendations are generated based on:

1. **Cycle Position Analysis**:
   - Buy signals occur when multiple cycles are near their troughs
   - Sell signals occur when multiple cycles are near their peaks
   - Hold signals occur during mixed or unclear cycle positions

2. **Cycle Confluence**:
   - Higher confidence when multiple cycles align in the same direction
   - Lower confidence during periods of cycle conflict

3. **Strength Weighting**:
   - Stronger cycles have more influence on the recommendation
   - Weak or noisy cycles are given less weight

### Market Sentiment Analysis
The market sentiment analysis uses natural language processing techniques to analyze financial news:

1. **Text Extraction**:
   - Web scraping financial news sources using Trafilatura
   - Filtering content by relevance to markets or specific tickers
   - Preprocessing text to normalize and clean content

2. **Sentiment Detection**:
   - Keyword-based approach using predefined dictionaries of:
     - Bullish terms (e.g., "rally", "upgrade", "outperform")
     - Bearish terms (e.g., "decline", "downgrade", "underperform")
     - Neutral terms (e.g., "unchanged", "hold", "stable")
   - Term frequency analysis with weighted scoring
   - Context consideration for negations and qualifiers

3. **Sentiment Scoring**:
   - Calculation of bullish, bearish, and neutral percentages
   - Overall mood score on a 0-100 scale:
     - 0-30: Bearish
     - 30-70: Neutral
     - 70-100: Bullish
   - Scoring adjustment based on term importance and context

4. **Visual Representation**:
   - Interactive gauge chart using Plotly
   - Color-coded ranges (red for bearish, yellow for neutral, green for bullish)
   - Dynamic needle positioning based on calculated mood value

## Performance Considerations

### Time Complexity
- Data processing: O(n) where n is the number of price data points
- FFT computation: O(n log n) using SciPy's optimized implementation
- Cycle detection: O(m) where m is the number of frequency bins

### Space Complexity
- Analysis objects stored in PostgreSQL as JSON
- Approximately 100KB-500KB per analysis, depending on data size and number of plots

### Scalability
- The application is designed for single-user use cases
- For multi-user deployments, consider:
  - Implementing a job queue for asynchronous processing
  - Adding caching for frequently accessed analyses
  - Optimizing database queries and indexing

## Security Considerations

### Data Protection
- User-uploaded files are stored temporarily and processed immediately
- No sensitive user data is collected or stored
- Database credentials are stored as environment variables

### Input Validation
- File upload size is limited
- File extension and MIME type validation
- Ticker symbol validation against known exchanges

### Error Handling
- Comprehensive try/except blocks with specific error messages
- Logging of errors for debugging
- User-friendly error pages

## Deployment

### Environment Setup
Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_SECRET_KEY`: Secret key for session management

### Deployment Options
1. **Local Development**:
   - Flask development server
   - Local PostgreSQL instance

2. **Production Deployment**:
   - Gunicorn WSGI server
   - PostgreSQL database (managed or self-hosted)
   - Nginx reverse proxy (recommended)
   - SSL/TLS encryption

## Testing

### Unit Tests
- Test data processing functions with known sample data
- Test FFT analysis with synthesized signals of known frequency
- Test recommendation engine with edge cases

### Integration Tests
- Test CSV upload and processing flow
- Test API fetching and processing flow
- Test database storage and retrieval

### End-to-End Tests
- Test complete user workflows
- Test report generation and download

## Future Enhancements

### Algorithm Improvements
- Implement wavelet transform for better time-frequency localization
- Add adaptive cycle detection that accounts for changing market regimes
- Incorporate machine learning for improved cycle significance estimation

### Feature Additions
- User accounts for saving and comparing analyses
- Batch processing of multiple stocks
- Email notifications for cycle alerts
- Backtesting module to validate cycle-based strategies

### Performance Optimizations
- Implement caching for frequently requested data
- Optimize database queries with proper indexing
- Add background processing for large datasets

## Technology Stack Details

### Backend
- Python 3.8+
- Flask 2.0+ web framework
- SQLAlchemy 1.4+ ORM
- Pandas 1.3+ for data manipulation
- NumPy 1.20+ for numerical operations
- SciPy 1.7+ for FFT and signal processing
- Plotly 5.0+ for visualization generation
- yfinance for stock data API access
- gunicorn for WSGI server

### Frontend
- Bootstrap 5 for responsive design
- Plotly.js for interactive charts
- Custom CSS for styling
- JavaScript for client-side interactivity

### Database
- PostgreSQL 13+ with JSON support
- SQLAlchemy for ORM
- psycopg2 for PostgreSQL connection