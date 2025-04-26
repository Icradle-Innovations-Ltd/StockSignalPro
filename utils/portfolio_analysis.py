"""Portfolio analysis module for analyzing multiple stocks."""
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.api_fetcher import fetch_stock_data
from utils.data_processing import process_data, perform_fft, detect_cycles
from utils.visualization import convert_numpy_to_lists


def create_portfolio(name, description, stocks, allocations=None):
    """
    Create a new portfolio object ready for DB insertion.
    
    Args:
        name (str): Portfolio name
        description (str): Portfolio description
        stocks (list): List of stock tickers
        allocations (dict, optional): Dictionary mapping tickers to allocation percentages
        
    Returns:
        dict: Portfolio data dictionary
    """
    # Validate stocks
    if not isinstance(stocks, list) or not stocks:
        raise ValueError("Stocks must be a non-empty list of tickers")
    
    # Create default equal allocations if none provided
    if allocations is None:
        allocation_pct = 100.0 / len(stocks)
        allocations = {ticker: allocation_pct for ticker in stocks}
    else:
        # Validate allocations
        if not isinstance(allocations, dict):
            raise ValueError("Allocations must be a dictionary mapping tickers to percentages")
        
        # Check if allocations sum to 100%
        total_allocation = sum(allocations.values())
        if abs(total_allocation - 100.0) > 0.01:  # Allow small rounding errors
            raise ValueError(f"Allocations must sum to 100% (current total: {total_allocation}%)")
    
    return {
        'name': name,
        'description': description,
        'stocks': stocks,
        'allocations': allocations,
        'correlation_matrix': None,
        'portfolio_plot': None,
        'cycle_analysis': None
    }


def fetch_portfolio_data(stocks, period="2y"):
    """
    Fetch data for multiple stocks in a portfolio.
    
    Args:
        stocks (list): List of stock tickers
        period (str): Time period to fetch
        
    Returns:
        dict: Dictionary mapping tickers to DataFrames
    """
    import logging
    logger = logging.getLogger(__name__)
    
    stock_data = {}
    
    if not stocks:
        logger.error("No stocks provided to fetch_portfolio_data")
        return stock_data
    
    logger.info(f"Fetching portfolio data for tickers: {stocks}")
    
    valid_data_count = 0
    error_count = 0
    
    for ticker in stocks:
        try:
            logger.info(f"Fetching data for ticker: {ticker}")
            df = fetch_stock_data(ticker, period=period)
            
            if df is not None and not df.empty:
                stock_data[ticker] = df
                valid_data_count += 1
                logger.info(f"Successfully fetched data for {ticker}, shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")
            else:
                logger.error(f"No data returned for ticker: {ticker}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            error_count += 1
    
    logger.info(f"Portfolio data fetch complete. Success: {valid_data_count}, Errors: {error_count}")
    
    return stock_data


def calculate_correlation_matrix(stock_data):
    """
    Calculate correlation matrix between stocks.
    
    Args:
        stock_data (dict): Dictionary mapping tickers to DataFrames
        
    Returns:
        DataFrame: Correlation matrix
    """
    # Extract prices from each dataframe
    price_data = {}
    
    for ticker, df in stock_data.items():
        if 'price' in df.columns:
            price_data[ticker] = df['price']
        elif 'Close' in df.columns:
            price_data[ticker] = df['Close']
    
    # Create a dataframe with all price series
    prices_df = pd.DataFrame(price_data)
    
    # Calculate correlation matrix
    correlation_matrix = prices_df.corr()
    
    return correlation_matrix


def create_correlation_heatmap(correlation_matrix):
    """
    Create a correlation heatmap visualization.
    
    Args:
        correlation_matrix (DataFrame): Correlation matrix
        
    Returns:
        dict: Plotly figure as JSON
    """
    fig = px.imshow(
        correlation_matrix,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        color_continuous_scale=px.colors.diverging.RdBu_r,
        zmin=-1, zmax=1,
        text_auto='.2f'
    )
    
    fig.update_layout(
        title="Stock Price Correlation Matrix",
        xaxis_title="",
        yaxis_title="",
        coloraxis_colorbar=dict(
            title="Correlation",
            titleside="right"
        ),
        height=500,
        width=700,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return json.loads(fig.to_json())


def analyze_portfolio_cycles(stock_data):
    """
    Analyze dominant cycles across multiple stocks.
    
    Args:
        stock_data (dict): Dictionary mapping tickers to DataFrames
        
    Returns:
        dict: Dictionary with cycle analysis results
    """
    cycle_results = {}
    common_cycles = {}
    
    for ticker, df in stock_data.items():
        # Process data
        processed_df = process_data(df)
        
        # Perform FFT analysis
        fft_results = perform_fft(processed_df)
        
        # Detect dominant cycles
        dominant_cycles = detect_cycles(fft_results)
        
        # Store cycles for this ticker
        cycle_results[ticker] = {
            'dominant_cycles': dominant_cycles
        }
        
        # Track cycle periods for finding common cycles
        for cycle in dominant_cycles:
            period = cycle['period']
            if period not in common_cycles:
                common_cycles[period] = []
            common_cycles[period].append({
                'ticker': ticker,
                'amplitude': cycle['amplitude'],
                'strength': cycle['strength'],
                'phase': cycle['phase']
            })
    
    # Identify truly common cycles (appearing in at least 2 stocks)
    shared_cycles = {period: stocks for period, stocks in common_cycles.items() if len(stocks) >= 2}
    
    # Sort shared cycles by how many stocks they appear in
    sorted_shared_cycles = sorted(
        shared_cycles.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    return {
        'individual_cycles': cycle_results,
        'shared_cycles': dict(sorted_shared_cycles)
    }


def create_portfolio_cycle_chart(cycle_analysis, stock_data):
    """
    Create a visualization of common cycles across the portfolio.
    
    Args:
        cycle_analysis (dict): Results from analyze_portfolio_cycles
        stock_data (dict): Dictionary mapping tickers to DataFrames
        
    Returns:
        dict: Plotly figure as JSON
    """
    shared_cycles = cycle_analysis.get('shared_cycles', {})
    
    if not shared_cycles:
        # Create empty figure with message if no shared cycles
        fig = go.Figure()
        fig.add_annotation(
            text="No common cycles detected across portfolio stocks",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return json.loads(fig.to_json())
    
    # Get the top shared cycles (up to 3)
    top_cycles = list(shared_cycles.items())[:3]
    
    # Create subplots for each top shared cycle
    fig = make_subplots(
        rows=len(top_cycles),
        cols=1,
        subplot_titles=[f"{period:.1f}-Day Cycle (Found in {len(stocks)} stocks)" 
                        for period, stocks in top_cycles]
    )
    
    # Add data for each cycle
    for i, (period, stocks) in enumerate(top_cycles, 1):
        # Sort stocks by cycle strength
        sorted_stocks = sorted(stocks, key=lambda x: x['strength'], reverse=True)
        
        # Add a bar for each stock showing the cycle strength
        ticker_list = [stock['ticker'] for stock in sorted_stocks]
        strength_list = [stock['strength'] for stock in sorted_stocks]
        
        fig.add_trace(
            go.Bar(
                x=ticker_list,
                y=strength_list,
                name=f"{period:.1f}-Day Cycle",
                text=[f"{s:.2f}" for s in strength_list],
                textposition="auto",
                marker_color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
            ),
            row=i, col=1
        )
        
        # Update y-axis title
        fig.update_yaxes(title_text="Cycle Strength", row=i, col=1)
    
    # Update layout
    fig.update_layout(
        title="Common Market Cycles Across Portfolio",
        showlegend=False,
        height=300 * len(top_cycles),
        width=800,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return json.loads(fig.to_json())


def create_portfolio_performance_chart(stock_data, allocations=None):
    """
    Create a performance chart for the portfolio.
    
    Args:
        stock_data (dict): Dictionary mapping tickers to DataFrames
        allocations (dict, optional): Dictionary mapping tickers to allocation percentages
        
    Returns:
        dict: Plotly figure as JSON
    """
    # Check if we have data
    if not stock_data:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No stock data available for portfolio",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return json.loads(fig.to_json())
    
    # Create equal allocations if none provided
    if allocations is None:
        allocation_pct = 100.0 / len(stock_data)
        allocations = {ticker: allocation_pct for ticker in stock_data.keys()}
    
    # Convert allocations to 0-1 scale
    weights = {ticker: pct / 100.0 for ticker, pct in allocations.items()}
    
    # Find common date range
    start_dates = [df.index.min() for df in stock_data.values() if not df.empty]
    end_dates = [df.index.max() for df in stock_data.values() if not df.empty]
    
    if not start_dates or not end_dates:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for portfolio analysis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return json.loads(fig.to_json())
    
    common_start = max(start_dates)
    common_end = min(end_dates)
    
    # Normalize each stock to starting value of 100
    normalized_data = {}
    
    for ticker, df in stock_data.items():
        if df.empty:
            continue
            
        # Filter to common date range
        filtered_df = df[(df.index >= common_start) & (df.index <= common_end)]
        
        if filtered_df.empty:
            continue
            
        # Get price column
        if 'price' in filtered_df.columns:
            price_col = 'price'
        elif 'Close' in filtered_df.columns:
            price_col = 'Close'
        else:
            continue
            
        # Normalize to 100
        first_price = filtered_df[price_col].iloc[0]
        normalized_data[ticker] = filtered_df[price_col] / first_price * 100
    
    # Create dataframe with all normalized prices
    if not normalized_data:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Could not normalize stock data for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return json.loads(fig.to_json())
        
    norm_df = pd.DataFrame(normalized_data)
    
    # Calculate portfolio performance
    portfolio_perf = pd.Series(0.0, index=norm_df.index)
    
    for ticker in norm_df.columns:
        if ticker in weights:
            portfolio_perf += norm_df[ticker] * weights.get(ticker, 0)
    
    # Create figure
    fig = go.Figure()
    
    # Add each stock
    for ticker in norm_df.columns:
        fig.add_trace(
            go.Scatter(
                x=norm_df.index,
                y=norm_df[ticker],
                mode='lines',
                name=f"{ticker} ({weights.get(ticker, 0)*100:.1f}%)",
                line=dict(width=1, dash='dash'),
                opacity=0.7
            )
        )
    
    # Add portfolio performance
    fig.add_trace(
        go.Scatter(
            x=portfolio_perf.index,
            y=portfolio_perf,
            mode='lines',
            name='Portfolio',
            line=dict(width=3, color='black')
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Portfolio Performance (Normalized to 100)",
        xaxis_title="Date",
        yaxis_title="Value (Starting at 100)",
        legend_title="Components",
        height=600,
        width=900,
        hovermode="x unified"
    )
    
    return json.loads(fig.to_json())