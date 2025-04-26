import pandas as pd
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)

def process_data(df):
    """Process and clean the input data.
    
    Args:
        df (DataFrame): Input dataframe with stock data
        
    Returns:
        DataFrame: Processed dataframe with date and price columns
    """
    try:
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Ensure we have a date column
        if 'date' not in df.columns:
            # Try to find a date-like column
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                df.rename(columns={date_cols[0]: 'date'}, inplace=True)
            else:
                raise ValueError("No date column found")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df.sort_values('date', inplace=True)
        
        # Ensure we have a price column
        if 'price' not in df.columns:
            # Try to find a price-like column
            price_cols = [col for col in df.columns if 'price' in col.lower() or 'close' in col.lower()]
            if price_cols:
                df.rename(columns={price_cols[0]: 'price'}, inplace=True)
            else:
                raise ValueError("No price column found")
        
        # Convert price to float
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Remove any rows with NaN values
        df.dropna(subset=['date', 'price'], inplace=True)
        
        # Reset index
        df.reset_index(drop=True, inplace=True)
        
        return df
        
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        raise

def perform_fft(df):
    """Perform Fast Fourier Transform on the price data.
    
    Args:
        df (DataFrame): Processed dataframe with price data
        
    Returns:
        dict: FFT results including frequencies, amplitudes, and phases
    """
    try:
        # Get the price data
        prices = df['price'].values
        
        # Ensure we have enough data points
        if len(prices) < 2:
            raise ValueError("Not enough data points for FFT analysis")
            
        # Remove any NaN values by interpolation
        if np.isnan(prices).any():
            prices = pd.Series(prices).interpolate().values
        
        # Apply a window function to reduce spectral leakage
        window = signal.windows.hann(len(prices))
        windowed_prices = prices * window
        
        # Perform FFT
        fft_result = np.fft.rfft(windowed_prices)
        
        # Calculate frequencies
        n = len(prices)
        sample_freq = 1  # 1 sample per day
        freqs = np.fft.rfftfreq(n, d=1/sample_freq)
        
        # Calculate periods (in days)
        periods = np.zeros_like(freqs)
        non_zero_freqs = freqs != 0
        periods[non_zero_freqs] = 1 / freqs[non_zero_freqs]
        
        # Calculate amplitudes (normalized)
        amplitudes = np.abs(fft_result) / (n/2)
        
        # Calculate phases
        phases = np.angle(fft_result)
        
        # Create results dictionary
        fft_results = {
            'frequencies': freqs[1:],  # Skip the DC component
            'periods': periods[1:],    # Skip the DC component
            'amplitudes': amplitudes[1:],  # Skip the DC component
            'phases': phases[1:],  # Skip the DC component
            'original_prices': prices.tolist(),
            'windowed_prices': windowed_prices.tolist()
        }
        
        return fft_results
    
    except Exception as e:
        logger.error(f"Error in FFT analysis: {str(e)}")
        raise

def detect_cycles(fft_results, min_period=2, max_period=252, strength_threshold=0.1):
    """Detect dominant cycles from FFT results.
    
    Args:
        fft_results (dict): Results from the FFT analysis
        min_period (int): Minimum period to consider (in days)
        max_period (int): Maximum period to consider (in days)
        strength_threshold (float): Minimum relative strength to consider a cycle
        
    Returns:
        list: List of dictionaries containing cycle information
    """
    try:
        periods = fft_results['periods']
        amplitudes = fft_results['amplitudes']
        phases = fft_results['phases']
        
        # Filter by period range
        # Convert to numpy arrays if they're lists (ensures proper comparison)
        if isinstance(periods, list):
            periods = np.array(periods)
        if isinstance(amplitudes, list):
            amplitudes = np.array(amplitudes)
        if isinstance(phases, list):
            phases = np.array(phases)
            
        mask = (periods >= min_period) & (periods <= max_period)
        filtered_periods = periods[mask]
        filtered_amplitudes = amplitudes[mask]
        filtered_phases = phases[mask]
        
        # Find the maximum amplitude
        if isinstance(filtered_amplitudes, list):
            max_amplitude = max(filtered_amplitudes) if filtered_amplitudes else 1 
        else:
            max_amplitude = np.max(filtered_amplitudes) if len(filtered_amplitudes) > 0 else 1
        
        # Calculate relative strengths
        # Handle the case where filtered_amplitudes might be a list
        if isinstance(filtered_amplitudes, list):
            filtered_amplitudes_np = np.array(filtered_amplitudes)
            relative_strengths = filtered_amplitudes_np / max_amplitude
        else:
            relative_strengths = filtered_amplitudes / max_amplitude
        
        # Identify dominant cycles (above strength threshold)
        # Ensure we're working with numpy arrays
        if isinstance(relative_strengths, list):
            relative_strengths = np.array(relative_strengths)
            
        dominant_indices = np.where(relative_strengths >= strength_threshold)[0]
        
        # Sort by strength (amplitude)
        sorted_indices = dominant_indices[np.argsort(-filtered_amplitudes[dominant_indices])]
        
        # Collect cycle information
        dominant_cycles = []
        for idx in sorted_indices:
            period = filtered_periods[idx]
            amplitude = filtered_amplitudes[idx]
            phase = filtered_phases[idx]
            
            # Calculate current phase position
            # This is a simplified approximation
            current_phase_position = (phase + np.pi) / (2 * np.pi)
            days_until_next_peak = period * (1 - current_phase_position)
            days_until_next_trough = period * (0.5 - current_phase_position)
            if days_until_next_trough < 0:
                days_until_next_trough += period
            
            dominant_cycles.append({
                'length': round(period, 1),
                'strength': round(relative_strengths[idx], 3),
                'amplitude': round(amplitude, 3),
                'phase': round(phase, 3),
                'current_position': round(current_phase_position, 2),
                'days_to_peak': round(days_until_next_peak, 1),
                'days_to_trough': round(days_until_next_trough, 1)
            })
        
        return dominant_cycles
    
    except Exception as e:
        logger.error(f"Error in cycle detection: {str(e)}")
        raise
