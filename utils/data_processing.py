import pandas as pd
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)

def process_data(df):
    """Process and clean the input data for FFT analysis.
    
    Args:
        df (DataFrame): Input dataframe with date and price columns
        
    Returns:
        DataFrame: Processed dataframe ready for FFT analysis
    """
    try:
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Standardize column names
        df.columns = [col.lower() for col in df.columns]
        
        # Ensure we have a date column
        if 'date' not in df.columns:
            if 'time' in df.columns:
                df.rename(columns={'time': 'date'}, inplace=True)
            else:
                # Try to find a date-like column
                date_cols = [col for col in df.columns if 'date' in col or 'time' in col]
                if date_cols:
                    df.rename(columns={date_cols[0]: 'date'}, inplace=True)
                else:
                    raise ValueError("Could not identify a date column in the data")
        
        # Ensure date is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        # Drop rows with missing dates
        df.dropna(subset=['date'], inplace=True)
        
        # Sort by date
        df.sort_values('date', inplace=True)
        
        # Find price column
        price_cols = [col for col in df.columns if 'price' in col or 'close' in col]
        if price_cols:
            price_col = price_cols[0]
        else:
            # If no obvious price column, try to find a numeric column that's not date
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col != 'date']
            if numeric_cols:
                price_col = numeric_cols[0]
            else:
                raise ValueError("Could not identify a price column in the data")
        
        # Ensure price column is numeric
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        
        # Drop rows with missing prices
        df.dropna(subset=[price_col], inplace=True)
        
        # Reset index
        df.reset_index(drop=True, inplace=True)
        
        # Standardize to just the columns we need
        result_df = pd.DataFrame({
            'date': df['date'],
            'price': df[price_col]
        })
        
        # Add additional columns that might be useful
        result_df['day_of_week'] = result_df['date'].dt.dayofweek
        result_df['is_weekday'] = result_df['day_of_week'] < 5
        
        # Optional: detrend the data to focus on cycles rather than trends
        # result_df['detrended_price'] = signal.detrend(result_df['price'])
        
        return result_df
    
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
        
        # Apply a window function to reduce spectral leakage
        window = signal.windows.hann(len(prices))
        windowed_prices = prices * window
        
        # Perform FFT
        fft_result = np.fft.rfft(windowed_prices)
        
        # Calculate frequencies
        # The sampling frequency is 1 sample per day
        n = len(prices)
        sample_freq = 1  # 1 sample per day
        freqs = np.fft.rfftfreq(n, d=1/sample_freq)
        
        # Calculate amplitudes (normalized by dividing by n/2)
        amplitudes = np.abs(fft_result) / (n/2)
        
        # Calculate phases
        phases = np.angle(fft_result)
        
        # Convert frequencies to periods (in days)
        periods = 1 / freqs[1:]  # Skip the DC component (index 0)
        
        # Convert NumPy arrays to Python lists for JSON serialization
        def convert_numpy_to_lists(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_to_lists(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_to_lists(item) for item in obj]
            elif isinstance(obj, (np.int64, np.int32, np.float64, np.float32)):
                return float(obj) if isinstance(obj, (np.float64, np.float32)) else int(obj)
            else:
                return obj
        
        # Pack results
        fft_results = {
            'frequencies': freqs[1:],  # Skip the DC component
            'periods': periods,
            'amplitudes': amplitudes[1:],  # Skip the DC component
            'phases': phases[1:],  # Skip the DC component
            'original_prices': prices,
            'windowed_prices': windowed_prices
        }
        
        # Convert to JSON serializable format
        fft_results = convert_numpy_to_lists(fft_results)
        
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
        mask = (periods >= min_period) & (periods <= max_period)
        filtered_periods = periods[mask]
        filtered_amplitudes = amplitudes[mask]
        filtered_phases = phases[mask]
        
        # Find the maximum amplitude
        max_amplitude = np.max(filtered_amplitudes) if len(filtered_amplitudes) > 0 else 1
        
        # Calculate relative strengths
        relative_strengths = filtered_amplitudes / max_amplitude
        
        # Identify dominant cycles (above strength threshold)
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
