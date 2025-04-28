import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import json
from scipy import signal
from datetime import datetime

logger = logging.getLogger(__name__)

# Helper function to ensure JSON serializable data
def convert_numpy_to_lists(obj):
    if isinstance(obj, np.ndarray):
        # Convert NaN to None for JSON serialization
        return [convert_numpy_to_lists(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_lists(item) for item in obj]
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (np.datetime64, datetime)):
        return pd.Timestamp(obj).isoformat()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

def create_time_series_plot(df):
    """Create an interactive time series plot of the price data.
    
    Args:
        df (DataFrame): Processed dataframe with price data
        
    Returns:
        dict: Plotly figure as JSON for rendering in the browser
    """
    try:
        # Create figure
        fig = go.Figure()
        
        # Add trace for price data
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color='rgba(49, 130, 189, 1)'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y:.2f}<extra></extra>'
        ))
        
        # Add a 7-day moving average
        df['ma7'] = df['price'].rolling(window=7).mean()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ma7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='rgba(255, 127, 14, 1)', dash='dot'),
            hovertemplate='<b>Date:</b> %{x}<br><b>7-Day MA:</b> %{y:.2f}<extra></extra>'
        ))
        
        # Add a 30-day moving average
        df['ma30'] = df['price'].rolling(window=30).mean()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ma30'],
            mode='lines',
            name='30-Day MA',
            line=dict(color='rgba(214, 39, 40, 1)', dash='dot'),
            hovertemplate='<b>Date:</b> %{x}<br><b>30-Day MA:</b> %{y:.2f}<extra></extra>'
        ))
        
        # Update layout with more detailed information
        fig.update_layout(
            title={
                'text': 'Historical Price Data with Moving Averages',
                'font': {'size': 24}
            },
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),

            margin=dict(l=40, r=40, t=100, b=160),
            template='plotly_white',
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            annotations=[
                dict(
                    text='Blue line shows actual price<br>Orange dotted line shows 7-day moving average (short-term trend)<br>Red dotted line shows 30-day moving average (long-term trend)',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,

                    y=-0.45,
                    align='left'
                )
            ]
        )
        
        # Return the figure as a JSON serializable object
        fig_dict = fig.to_dict()
        return convert_numpy_to_lists(fig_dict)
    
    except Exception as e:
        logger.error(f"Error creating time series plot: {str(e)}")
        raise

def create_frequency_plot(fft_results):
    """Create an interactive plot of the frequency domain analysis.
    
    Args:
        fft_results (dict): Results from the FFT analysis
        
    Returns:
        dict: Plotly figure as JSON for rendering in the browser
    """
    try:
        # Unpack FFT results and ensure they're numpy arrays
        periods = np.array(fft_results['periods'])
        amplitudes = np.array(fft_results['amplitudes'])
        
        # Filter to relevant periods (2 days to 252 days/1 year)
        mask = (periods >= 2) & (periods <= 252)
        filtered_periods = periods[mask]
        filtered_amplitudes = amplitudes[mask]
        
        if len(filtered_periods) == 0 or len(filtered_amplitudes) == 0:
            raise ValueError("No valid data points for frequency plot")
        
        # Create figure
        fig = go.Figure()
        
        # Add trace for power spectrum
        fig.add_trace(go.Scatter(
            x=filtered_periods,
            y=filtered_amplitudes,
            mode='lines',
            name='Power Spectrum',
            line=dict(color='rgba(49, 130, 189, 1)'),
            hovertemplate='<b>Period:</b> %{x:.1f} days<br><b>Amplitude:</b> %{y:.4f}<extra></extra>'
        ))
        
        # Find peaks for annotation
        peak_indices = signal.find_peaks(filtered_amplitudes, height=np.max(filtered_amplitudes)*0.1)[0]
        peak_periods = filtered_periods[peak_indices]
        peak_amplitudes = filtered_amplitudes[peak_indices]
        
        # Sort peaks by amplitude and take top 5
        peak_order = np.argsort(-peak_amplitudes)[:5]
        top_periods = peak_periods[peak_order]
        top_amplitudes = peak_amplitudes[peak_order]
        
        # Add markers and annotations for peaks
        fig.add_trace(go.Scatter(
            x=top_periods,
            y=top_amplitudes,
            mode='markers+text',
            name='Major Cycles',
            marker=dict(
                color='rgba(255, 127, 14, 1)',
                size=10
            ),
            text=[f'{p:.1f}d' for p in top_periods],
            textposition='top center',
            hovertemplate='<b>Period:</b> %{x:.1f} days<br><b>Amplitude:</b> %{y:.4f}<extra></extra>'
        ))
        
        # Update layout with more detailed information
        fig.update_layout(
            title={
                'text': 'Frequency Domain Analysis - Price Cycles',
                'font': {'size': 24}
            },
            xaxis_title='Period (days)',
            yaxis_title='Amplitude',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),

            margin=dict(l=40, r=40, t=100, b=180),
            template='plotly_white',
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            annotations=[
                dict(
                    text='Blue line shows the strength of price cycles at different periods<br>Orange dots highlight the most significant cycles<br>Higher amplitude indicates stronger price patterns at that period<br>X-axis uses logarithmic scale to better display cycle lengths',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,

                    y=-0.5,
                    align='left'
                )
            ]
        )
        
        # Use log scale for x-axis to better show the distribution of periods
        fig.update_xaxes(type='log')
        
        # Return the figure as a JSON serializable object
        fig_dict = fig.to_dict()
        return convert_numpy_to_lists(fig_dict)
    
    except Exception as e:
        logger.error(f"Error creating frequency plot: {str(e)}")
        raise

def create_forecast_plot(df, dominant_cycles, forecast_days=30):
    """Create a forecast plot based on detected cycles.
    
    Args:
        df (DataFrame): Processed dataframe with price data
        dominant_cycles (list): List of dominant cycles detected
        forecast_days (int): Number of days to forecast
        
    Returns:
        dict: Plotly figure as JSON for rendering in the browser
    """
    try:
        # Get the last price and date
        last_price = df['price'].iloc[-1]
        last_date = df['date'].iloc[-1]
        
        # Create forecast dates
        forecast_dates = pd.date_range(start=last_date, periods=forecast_days + 1)[1:]
        
        # Create base forecast (flat line at last price)
        forecast_prices = np.ones(forecast_days) * last_price
        
        # Add the effect of each dominant cycle
        for cycle in dominant_cycles[:3]:  # Use top 3 dominant cycles
            period = cycle['length']
            amplitude = cycle['amplitude'] * last_price  # Scale amplitude relative to last price
            phase = cycle['phase']
            
            # Calculate the contribution of this cycle to each forecast day
            for i in range(forecast_days):
                day = i + 1  # Start from day after last date
                # Calculate the phase for this day
                t = 2 * np.pi * day / period
                cycle_effect = amplitude * np.cos(t + phase)
                forecast_prices[i] += cycle_effect
        
        # Create figure
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        # Add historical price data
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['price'],
                mode='lines',
                name='Historical',
                line=dict(color='rgba(49, 130, 189, 1)'),
                hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y:.2f}<extra></extra>'
            )
        )
        
        # Add forecast
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_prices,
                mode='lines',
                name='Forecast',
                line=dict(color='rgba(255, 127, 14, 1)', dash='dash'),
                hovertemplate='<b>Date:</b> %{x}<br><b>Forecast:</b> %{y:.2f}<extra></extra>'
            )
        )
        
        # Add a vertical line at the forecast start
        fig.add_shape(
            type="line",
            x0=last_date,
            y0=min(df['price'].min(), forecast_prices.min()) * 0.95,
            x1=last_date,
            y1=max(df['price'].max(), forecast_prices.max()) * 1.05,
            line=dict(
                color="Gray",
                width=2,
                dash="dot",
            )
        )
        
        # Add annotation for forecast start
        fig.add_annotation(
            x=last_date,
            y=last_price,
            text="Forecast Start",
            showarrow=True,
            arrowhead=1,
            ax=50,
            ay=0
        )
        
        # Update layout with more detailed information
        fig.update_layout(
            title={
                'text': 'Price Forecast Based on Detected Cycles',
                'font': {'size': 24}
            },
            xaxis_title='Date',
            yaxis_title='Price',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),

            margin=dict(l=40, r=40, t=100, b=180),
            template='plotly_white',
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='rgba(255,255,255,1)',
            annotations=[
                dict(
                    text='Blue line shows historical price data<br>Orange dashed line shows forecasted prices based on detected cycles<br>Gray dotted line marks the start of the forecast period<br>Forecast combines the effects of the top 3 dominant cycles',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,

                    y=-0.5,
                    align='left'
                )
            ]
        )
        
        # Return the figure as a JSON serializable object
        fig_dict = fig.to_dict()
        return convert_numpy_to_lists(fig_dict)
    
    except Exception as e:
        logger.error(f"Error creating forecast plot: {str(e)}")
        raise