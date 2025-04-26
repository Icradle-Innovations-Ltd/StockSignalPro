# Stock Market Signal Processing Web App

A web application that leverages Fast Fourier Transform (FFT) algorithms to analyze and predict stock market cycles with advanced data visualization and recommendation capabilities.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This application applies signal processing techniques to stock market data to identify hidden market cycles and generate trading recommendations. By utilizing Fast Fourier Transform (FFT) algorithms, the app can detect periodic patterns in price data that might not be visible through traditional technical analysis methods.

Users can upload their own CSV data files or enter a stock ticker symbol to fetch real-time market data. The application then processes this data, identifies dominant cycles, and provides actionable insights with confidence ratings.

## Features

- **Data Import Options**:
  - Upload CSV files with historical price data
  - Fetch live data by entering stock ticker symbols
  - Select time periods for analysis (1yr, 2yrs, 5yrs, etc.)

- **Advanced Technical Analysis**:
  - Fast Fourier Transform (FFT) analysis to detect market cycles
  - Identification of dominant cycles with period length and strength metrics
  - Phase analysis to determine current position within cycles
  - Market sentiment analysis based on financial news

- **Trading Recommendations**:
  - Buy/Hold/Sell recommendations with confidence ratings
  - Context-aware analysis based on current market conditions
  - Reasoning behind each recommendation

- **Interactive Visualizations**:
  - Time series plots with moving averages
  - Frequency domain (power spectrum) analysis
  - Price forecasting based on detected cycles
  - Market sentiment gauge charts with bullish/bearish indicators

- **Export Options**:
  - Generate PDF reports of analysis results
  - Download CSV data of processed results

- **Database Integration**:
  - PostgreSQL database for storing analysis results
  - Persistent storage for retrieving past analyses

## Technical Architecture

The application is built using a modern web stack with the following components:

- **Backend**:
  - Python Flask web framework
  - SQLAlchemy ORM for database operations
  - NumPy and SciPy for numerical computations and FFT analysis
  - Pandas for data manipulation and processing
  - PostgreSQL database for data persistence
  - Trafilatura for web content extraction
  - Natural language processing for sentiment analysis

- **Frontend**:
  - Bootstrap 5 for responsive UI components
  - Plotly.js for interactive data visualizations
  - Custom CSS for styling
  - JavaScript for client-side interactions

- **Data Processing Pipeline**:
  1. Data acquisition (CSV upload or API fetch)
  2. Data cleaning and preprocessing
  3. FFT analysis and cycle detection
  4. Trading recommendation generation
  5. Market sentiment analysis (scraping and processing financial news)
  6. Visualization creation (including sentiment gauge charts)
  7. Results storage and presentation

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- pip package manager

### Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/stock-market-signal-processing.git
   cd stock-market-signal-processing
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   export DATABASE_URL=postgresql://username:password@localhost/dbname
   # On Windows: set DATABASE_URL=postgresql://username:password@localhost/dbname
   ```

5. Initialize the database:
   ```
   python initialize_db.py
   ```

6. Start the application:
   ```
   python main.py
   ```
   
7. Access the application at http://localhost:5000

## Usage

### Analyzing Stock Data with CSV Upload
1. Prepare a CSV file with date and price columns (format: date,price)
2. Navigate to the home page
3. Click "Upload CSV File" and select your file
4. Click "Analyze Stock Data"
5. View the results, including detected cycles and recommendations

### Analyzing Stock Data with Ticker Symbol
1. Navigate to the home page
2. Enter a valid stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
3. Select the desired time period
4. Click "Analyze Stock Data"
5. View the results, including detected cycles and recommendations

### Understanding the Results
- **Time Series Chart**: Shows historical price data with moving averages
- **Recommendation**: Displays Buy/Hold/Sell advice with confidence rating
- **Dominant Cycles**: Lists detected market cycles with their periods and strength
- **Frequency Analysis**: Visualizes the power spectrum of detected cycles
- **Price Forecast**: Projects potential price movement based on cycle analysis
- **Market Sentiment**: Displays bullish/bearish/neutral gauge based on financial news
- **Ticker Sentiment**: Shows sentiment analysis specific to individual stocks

### Exporting Results
- Click "Generate PDF Report" to create a downloadable PDF document
- Click "Download CSV" to export the analysis data in CSV format

## File Structure

```
stock-market-signal-processing/
├── app.py                  # Main application file with routes
├── main.py                 # Entry point for the application
├── models.py               # Database models
├── utils/
│   ├── __init__.py         # Package initialization
│   ├── api_fetcher.py      # Stock data API integration
│   ├── data_processing.py  # Data cleaning and FFT analysis
│   ├── decision_engine.py  # Trading recommendation logic
│   ├── visualization.py    # Chart and plot generation
│   ├── sentiment_analysis.py # Market sentiment processing
│   └── web_scraper.py      # Web content extraction for news
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── assets/             # Images and other assets
├── templates/
│   ├── index.html          # Home page template
│   ├── results.html        # Analysis results template
│   ├── report.html         # PDF report template
│   ├── market_sentiment.html # Market sentiment analysis page
│   └── ticker_sentiment.html # Ticker-specific sentiment page
├── uploads/                # Temporary storage for uploaded files
├── sample_stock_data.csv   # Example data file
└── README.md               # Project documentation
```

## How It Works

### Fast Fourier Transform (FFT) Analysis
The application applies FFT to transform time-domain price data into the frequency domain. This mathematical technique helps identify cyclical patterns in seemingly random price movements.

1. **Data Preprocessing**:
   - Convert dates to a numerical time index
   - Normalize price data
   - Apply detrending to remove long-term trends

2. **FFT Application**:
   - Calculate frequencies and amplitudes using SciPy's FFT function
   - Filter to relevant frequency ranges (2-252 days)
   - Identify peaks in the frequency spectrum

3. **Cycle Detection**:
   - Determine periods of dominant cycles (e.g., 20-day, 55-day, 90-day cycles)
   - Calculate strength and phase of each cycle
   - Rank cycles by significance

### Trading Recommendation Generation
The application generates recommendations based on detected cycles and their current position:

1. **Phase Analysis**:
   - Determine where in each cycle the current price is located
   - Calculate momentum and trend direction

2. **Multi-cycle Approach**:
   - Consider interactions between different cycle lengths
   - Weight cycles by strength and reliability

3. **Confidence Calculation**:
   - Assign confidence based on cycle clarity and strength
   - Adjust recommendations based on confidence levels
   
### Market Sentiment Analysis
The application analyzes financial news and content to determine market sentiment:

1. **Data Collection**:
   - Scrape financial news from reputable sources
   - Extract relevant text content using Trafilatura
   - Optionally filter for specific ticker mentions

2. **Sentiment Processing**:
   - Analyze text for bullish/bearish/neutral keywords
   - Count and weight keyword occurrences
   - Calculate sentiment scores for each category
   
3. **Mood Determination**:
   - Combine sentiment scores into an overall mood
   - Classify as bullish, bearish, or neutral
   - Assign a numeric value between 0-100

### Visualization Creation
The application creates the following main types of visualizations:

1. **Time Series Plot**:
   - Historical price data with 7-day and 30-day moving averages
   - Interactive zooming and data inspection

2. **Frequency Domain Plot**:
   - Power spectrum showing cycle periods and amplitudes
   - Highlighted dominant cycles with period labels

3. **Forecast Plot**:
   - Price projection based on superposition of detected cycles
   - Confidence intervals for forecasted prices
   
4. **Sentiment Gauge Chart**:
   - Circular gauge showing market sentiment from bearish to bullish
   - Color-coded indicators (red for bearish, green for bullish)
   - Numeric sentiment score from 0 to 100

## API Reference

### Endpoints

#### `GET /`
- Home page with upload form and ticker search

#### `POST /upload`
- Processes uploaded CSV file or ticker input
- Parameters:
  - `file`: CSV file (optional)
  - `ticker`: Stock ticker symbol (optional)
  - `period`: Time period for analysis (optional, default: "2y")

#### `GET /results/<analysis_id>`
- Displays analysis results
- Parameters:
  - `analysis_id`: Unique identifier for the analysis

#### `GET /api/plot/<analysis_id>/<plot_type>`
- Returns JSON data for specified plot
- Parameters:
  - `analysis_id`: Unique identifier for the analysis
  - `plot_type`: Type of plot (time_series, frequency, forecast)

#### `GET /report/<analysis_id>`
- Generates PDF report of analysis
- Parameters:
  - `analysis_id`: Unique identifier for the analysis

#### `GET /download/<analysis_id>`
- Downloads CSV file of analysis results
- Parameters:
  - `analysis_id`: Unique identifier for the analysis
  
#### `GET /market-sentiment`
- Displays overall market sentiment analysis page
  
#### `GET /api/market-sentiment`
- Returns JSON data for market sentiment gauge
  
#### `GET /ticker-sentiment/<ticker>`
- Displays sentiment analysis for specific stock ticker
- Parameters:
  - `ticker`: Stock ticker symbol

### Models

#### Analysis
- `id`: Unique identifier (UUID)
- `ticker`: Stock ticker symbol
- `created_at`: Timestamp of analysis
- `source_type`: Data source ("file" or "api")
- `filename`: Name of uploaded file (if applicable)
- `data`: JSON data of processed stock data
- `recommendation`: JSON data of trading recommendation
- `dominant_cycles`: JSON data of detected cycles
- `time_series_plot`: JSON data for time series visualization
- `frequency_plot`: JSON data for frequency domain visualization
- `forecast_plot`: JSON data for forecast visualization

#### MarketSentiment
- `id`: Unique identifier (UUID)
- `ticker`: Stock ticker symbol (optional, for specific stocks)
- `created_at`: Timestamp of sentiment analysis
- `bullish_score`: Float value representing bullish sentiment (0-1)
- `bearish_score`: Float value representing bearish sentiment (0-1)
- `neutral_score`: Float value representing neutral sentiment (0-1)
- `mood`: String indicator ("bullish", "bearish", or "neutral")
- `mood_value`: Numeric value between 0-100 indicating sentiment
- `sentiment_gauge`: JSON data for gauge chart visualization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.