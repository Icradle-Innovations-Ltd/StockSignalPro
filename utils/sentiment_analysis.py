import logging
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from trafilatura import fetch_url, extract
from utils.web_scraper import get_website_text_content

logger = logging.getLogger(__name__)

# Define sentiment keywords and their weights
BULLISH_KEYWORDS = [
    'bullish', 'surge', 'rally', 'outperform', 'upgrade', 'upside', 
    'growth', 'buy', 'strong', 'positive', 'recovery', 'beat', 
    'exceeds', 'gain', 'rising', 'record high', 'breakthrough'
]

BEARISH_KEYWORDS = [
    'bearish', 'slump', 'decline', 'underperform', 'downgrade', 'downside', 
    'contraction', 'sell', 'weak', 'negative', 'recession', 'miss', 
    'below expectations', 'loss', 'falling', 'record low', 'breakdown'
]

NEUTRAL_KEYWORDS = [
    'neutral', 'steady', 'stable', 'hold', 'in-line', 'unchanged', 
    'flat', 'balanced', 'mixed', 'as expected', 'maintained', 'moderate'
]

NEWS_SOURCES = [
    'https://finance.yahoo.com/topic/stock-market-news/',
    'https://www.marketwatch.com/latest-news',
    'https://www.cnbc.com/markets/'
]

def analyze_text_sentiment(text):
    """
    Analyze sentiment of a text by counting occurrences of bullish, bearish, and neutral keywords.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Dictionary with sentiment scores and mood
    """
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Count keyword occurrences
    bullish_count = sum(text_lower.count(keyword.lower()) for keyword in BULLISH_KEYWORDS)
    bearish_count = sum(text_lower.count(keyword.lower()) for keyword in BEARISH_KEYWORDS)
    neutral_count = sum(text_lower.count(keyword.lower()) for keyword in NEUTRAL_KEYWORDS)
    
    # Calculate total occurrences
    total = bullish_count + bearish_count + neutral_count
    if total == 0:
        # No sentiment keywords found
        return {
            'bullish_score': 0,
            'bearish_score': 0,
            'neutral_score': 100,  # Default to neutral
            'mood': 'neutral',
            'mood_value': 50  # Middle of the scale
        }
    
    # Calculate percentages
    bullish_percent = (bullish_count / total) * 100
    bearish_percent = (bearish_count / total) * 100
    neutral_percent = (neutral_count / total) * 100
    
    # Determine overall mood
    if bullish_percent > bearish_percent and bullish_percent > neutral_percent:
        mood = 'bullish'
        # Scale from 66 to 100 (bullish range)
        mood_value = 66 + (bullish_percent / 100) * 34
    elif bearish_percent > bullish_percent and bearish_percent > neutral_percent:
        mood = 'bearish'
        # Scale from 0 to 33 (bearish range)
        mood_value = 33 - (bearish_percent / 100) * 33
    else:
        mood = 'neutral'
        # Scale from 33 to 66 (neutral range)
        mood_value = 33 + (neutral_percent / 100) * 33
    
    return {
        'bullish_score': round(bullish_percent, 1),
        'bearish_score': round(bearish_percent, 1),
        'neutral_score': round(neutral_percent, 1),
        'mood': mood,
        'mood_value': round(mood_value, 1)
    }

def fetch_market_news(source_url=None):
    """
    Fetch market news from a specific source or default sources.
    
    Args:
        source_url (str, optional): URL to fetch news from. If None, uses default sources.
        
    Returns:
        str: Combined text content from the news sources
    """
    combined_text = ""
    try:
        if source_url:
            # Fetch from specified source
            text = get_website_text_content(source_url)
            if text:
                combined_text += text
        else:
            # Fetch from all default sources
            for url in NEWS_SOURCES:
                try:
                    text = get_website_text_content(url)
                    if text:
                        combined_text += text
                except Exception as e:
                    logger.warning(f"Error fetching news from {url}: {str(e)}")
                    continue
        
        return combined_text
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        return ""

def get_market_sentiment(ticker=None, custom_news_text=None):
    """
    Get market sentiment based on news, optionally filtered for a specific ticker.
    
    Args:
        ticker (str, optional): Stock ticker to filter news for
        custom_news_text (str, optional): Custom news text to analyze instead of fetching
        
    Returns:
        dict: Sentiment analysis results
    """
    try:
        # Use custom text if provided, otherwise fetch news
        if custom_news_text:
            text_to_analyze = custom_news_text
        else:
            text_to_analyze = fetch_market_news()
            
            # If ticker is provided, filter for ticker-specific news
            if ticker:
                # Add ticker-specific news
                ticker_news_url = f"https://finance.yahoo.com/quote/{ticker}"
                ticker_news = get_website_text_content(ticker_news_url)
                if ticker_news:
                    text_to_analyze += ticker_news
        
        # Analyze sentiment
        if not text_to_analyze:
            logger.warning("No news text to analyze")
            # Return neutral sentiment as default
            return {
                'bullish_score': 0,
                'bearish_score': 0,
                'neutral_score': 100,
                'mood': 'neutral',
                'mood_value': 50,
                'timestamp': datetime.now().isoformat()
            }
        
        sentiment = analyze_text_sentiment(text_to_analyze)
        sentiment['timestamp'] = datetime.now().isoformat()
        
        return sentiment
    
    except Exception as e:
        logger.error(f"Error getting market sentiment: {str(e)}")
        # Return neutral sentiment on error
        return {
            'bullish_score': 0,
            'bearish_score': 0,
            'neutral_score': 100,
            'mood': 'neutral',
            'mood_value': 50,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def create_sentiment_gauge(sentiment):
    """
    Create a gauge chart for the sentiment mood.
    
    Args:
        sentiment (dict): Sentiment analysis results
        
    Returns:
        dict: Plotly figure as JSON for rendering in the browser
    """
    # Define the gauge steps and colors
    steps = [
        {'range': [0, 33], 'color': 'rgba(255, 99, 71, 0.8)'},  # Tomato red (Bearish)
        {'range': [33, 66], 'color': 'rgba(255, 215, 0, 0.8)'},  # Gold (Neutral)
        {'range': [66, 100], 'color': 'rgba(50, 205, 50, 0.8)'}  # Lime green (Bullish)
    ]
    
    # Get mood value from sentiment
    mood_value = sentiment.get('mood_value', 50)
    
    # Determine title based on mood
    mood = sentiment.get('mood', 'neutral').capitalize()
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = mood_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Market Sentiment: {mood}", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': mood_value
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        paper_bgcolor = "rgba(255,255,255,1)",
        font = {'color': "darkblue", 'family': "Arial"}
    )
    
    # Convert to JSON for JavaScript
    return fig.to_dict()