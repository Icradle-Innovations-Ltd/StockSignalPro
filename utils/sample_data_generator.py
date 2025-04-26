import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import io
import random

def generate_sample_stock_data(days=365, start_price=100, volatility=0.015, trend=0.0001, 
                               cycles=[(20, 0.05), (40, 0.03), (60, 0.04)], seed=None):
    """
    Generate sample stock price data with embedded cycles.
    
    Args:
        days (int): Number of trading days to generate
        start_price (float): Starting price for the stock
        volatility (float): Daily volatility (standard deviation)
        trend (float): Daily trend factor (positive for uptrend, negative for downtrend)
        cycles (list): List of tuples (period, amplitude) for embedded cycles
        seed (int): Random seed for reproducibility
        
    Returns:
        DataFrame: DataFrame with date and price columns
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate dates (business days only)
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days * 1.5)  # Add extra days to account for weekends/holidays
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    if len(date_range) > days:
        date_range = date_range[-days:]
    
    # Generate price data with random walk
    price = np.zeros(len(date_range))
    price[0] = start_price
    
    # Random component (geometric random walk)
    random_walk = np.random.normal(0, volatility, len(date_range))
    
    # Add trend and random component
    for i in range(1, len(date_range)):
        price[i] = price[i-1] * (1 + trend + random_walk[i])
    
    # Add cycles
    t = np.arange(len(date_range))
    for period, amplitude in cycles:
        # Random phase for each cycle
        phase = np.random.uniform(0, 2 * np.pi)
        cycle_component = amplitude * np.sin(2 * np.pi * t / period + phase)
        price = price * (1 + cycle_component)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'price': price
    })
    
    return df

def generate_sample_data_csv(stock_type='random', params=None):
    """
    Generate sample stock data and return as CSV string.
    
    Args:
        stock_type (str): Type of sample data to generate:
            'random': Completely random stock
            'bullish': Stock with upward trend
            'bearish': Stock with downward trend
            'volatile': High volatility stock
            'cyclical': Stock with strong cycles
            
        params (dict): Optional parameters to override defaults
        
    Returns:
        str: CSV string of the generated data
    """
    if params is None:
        params = {}
    
    # Base parameters
    days = params.get('days', 365)
    start_price = params.get('start_price', 100)
    
    # Define parameters based on stock type
    if stock_type == 'bullish':
        volatility = params.get('volatility', 0.015)
        trend = params.get('trend', 0.0008)  # Positive trend
        cycles = params.get('cycles', [(30, 0.03), (60, 0.04)])
        seed = params.get('seed', 42)
        
    elif stock_type == 'bearish':
        volatility = params.get('volatility', 0.015)
        trend = params.get('trend', -0.0005)  # Negative trend
        cycles = params.get('cycles', [(25, 0.02), (45, 0.03)])
        seed = params.get('seed', 123)
        
    elif stock_type == 'volatile':
        volatility = params.get('volatility', 0.025)  # Higher volatility
        trend = params.get('trend', 0.0001)
        cycles = params.get('cycles', [(15, 0.08), (45, 0.05)])
        seed = params.get('seed', 456)
        
    elif stock_type == 'cyclical':
        volatility = params.get('volatility', 0.012)
        trend = params.get('trend', 0.0002)
        cycles = params.get('cycles', [(20, 0.08), (40, 0.06), (60, 0.05)])  # Stronger cycles
        seed = params.get('seed', 789)
        
    else:  # 'random'
        volatility = params.get('volatility', 0.015)
        trend = params.get('trend', 0.0001)
        cycles = params.get('cycles', [(20, 0.04), (40, 0.03), (60, 0.02)])
        seed = params.get('seed', None)  # Truly random
    
    # Generate the data
    df = generate_sample_stock_data(
        days=days,
        start_price=start_price,
        volatility=volatility,
        trend=trend,
        cycles=cycles,
        seed=seed
    )
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, date_format='%Y-%m-%d')
    csv_string = csv_buffer.getvalue()
    
    return csv_string

def get_sample_data_info():
    """Returns information about the available sample data types."""
    return {
        'random': {
            'name': 'Random Stock',
            'description': 'A stock with random movement and moderate cycles',
            'properties': 'Moderate volatility, slight upward trend'
        },
        'bullish': {
            'name': 'Bullish Trend',
            'description': 'A stock with a strong upward trend',
            'properties': 'Moderate volatility, significant upward trend'
        },
        'bearish': {
            'name': 'Bearish Trend',
            'description': 'A stock with a downward trend',
            'properties': 'Moderate volatility, downward trend'
        },
        'volatile': {
            'name': 'Highly Volatile',
            'description': 'A stock with high day-to-day volatility',
            'properties': 'High volatility, short-term cycles'
        },
        'cyclical': {
            'name': 'Cyclical Stock',
            'description': 'A stock with very pronounced market cycles',
            'properties': 'Strong 20-day, 40-day, and 60-day cycles'
        }
    }

def sample_ticker_symbol():
    """Generate a random ticker symbol for sample data."""
    prefixes = ["SMPL", "TEST", "DEMO", "CYC", "SIM"]
    suffixes = ["", "X", "CO", "INC", "TECH"]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    return f"{prefix}{suffix}"