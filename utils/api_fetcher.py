import pandas as pd
import yfinance as yf
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_stock_data(ticker, period="2y"):
    """Fetch stock data for the given ticker.

    Args:
        ticker (str): Stock ticker symbol
        period (str): Period to fetch (default: 2y for 2 years)

    Returns:
        DataFrame: Processed dataframe with stock data
    """
    try:
        logger.info(f"Fetching data for {ticker} with period {period}")

        # Validate ticker format
        ticker = ticker.strip().upper()
        if not ticker or len(ticker) > 10:
            raise ValueError("Invalid ticker symbol")

        # Fetch data from Yahoo Finance with error handling
        stock = yf.Ticker(ticker)
        # Add a small delay to avoid rate limiting
        import time
        time.sleep(1)

        # Add delay before API call with exponential backoff
        max_retries = 3
        retry_delay = 2
        hist = None

        for attempt in range(max_retries):
            try:
                time.sleep(retry_delay * (attempt + 1))

                try:
                    # Try to get info first to validate the ticker
                    info = stock.info
                    if not info:
                        raise ValueError(f"Could not validate ticker {ticker}")

                    # Add delay between calls
                    time.sleep(1)

                    # Now fetch the historical data
                    hist = stock.history(period=period)

                    if not hist.empty:
                        break
                except Exception as e:
                    logger.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
                    if "Expecting value" in str(e):
                        # This usually means the API is rate limited or temporarily unavailable
                        time.sleep(retry_delay * 2)  # Double the delay for rate limit issues
                    if attempt == max_retries - 1:
                        raise ValueError(f"Failed to fetch data after {max_retries} attempts: Rate limit or API unavailability")


            except Exception as retry_error:
                logger.warning(f"Attempt {attempt + 1} failed: {str(retry_error)}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to fetch data after {max_retries} attempts: {str(retry_error)}")

        # Check if we got data
        if hist is None or hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        logger.info(f"Successfully fetched {len(hist)} rows for {ticker}")

        # Reset index to make Date a column
        hist = hist.reset_index()

        # Rename columns to match our expected format
        hist.rename(columns={
            'Date': 'date',
            'Close': 'price',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume'
        }, inplace=True)

        return hist

    except Exception as e:
        logger.error(f"Error in fetch_stock_data for {ticker}: {str(e)}")
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")

def search_tickers(query):
    """Search for ticker symbols matching the query.

    Args:
        query (str): Search query

    Returns:
        list: List of matching ticker symbols with company names
    """
    try:
        # This is a simplified version - in production, you would use a more robust ticker search API
        # For now, we'll return a static list for common tickers
        common_tickers = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOG': 'Alphabet Inc.',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com, Inc.',
            'FB': 'Meta Platforms, Inc.',
            'TSLA': 'Tesla, Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'V': 'Visa Inc.',
            'JNJ': 'Johnson & Johnson',
            'WMT': 'Walmart Inc.',
            'BAC': 'Bank of America Corporation',
            'PG': 'The Procter & Gamble Company',
            'MA': 'Mastercard Incorporated',
            'DIS': 'The Walt Disney Company',
            'NFLX': 'Netflix, Inc.',
            'XOM': 'Exxon Mobil Corporation',
            'T': 'AT&T Inc.',
            'INTC': 'Intel Corporation'
        }

        # Filter tickers based on query
        query = query.upper()
        matches = []

        for ticker, company in common_tickers.items():
            if query in ticker or query.lower() in company.lower():
                matches.append({'ticker': ticker, 'company': company})

        return matches

    except Exception as e:
        logger.error(f"Error searching tickers: {str(e)}")
        return []