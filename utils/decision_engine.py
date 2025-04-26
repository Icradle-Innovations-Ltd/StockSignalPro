import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_recommendation(df, dominant_cycles):
    """Generate trading recommendations based on detected cycles.
    
    Args:
        df (DataFrame): Processed dataframe with price data
        dominant_cycles (list): List of dominant cycles detected
        
    Returns:
        dict: Recommendation with action, confidence, and reasoning
    """
    try:
        # Initialize recommendation
        recommendation = {
            'action': 'HOLD',
            'confidence': 0.5,
            'reasoning': [],
            'details': []
        }
        
        # If no dominant cycles, return HOLD
        if not dominant_cycles:
            recommendation['reasoning'].append("No significant market cycles detected.")
            return recommendation
        
        # Get latest price data
        last_price = df['price'].iloc[-1]
        prev_price = df['price'].iloc[-2] if len(df) > 1 else last_price
        
        # Calculate recent price change
        recent_change = (last_price - prev_price) / prev_price
        
        # Check if we're near a cycle trough for BUY or peak for SELL
        buy_signals = 0
        sell_signals = 0
        total_weight = 0
        
        # Add details for each cycle
        for i, cycle in enumerate(dominant_cycles[:3]):  # Consider top 3 cycles
            weight = cycle['strength']
            total_weight += weight
            
            # Check if we're approaching a trough (good time to BUY)
            days_to_trough = cycle['days_to_trough']
            days_to_peak = cycle['days_to_peak']
            
            cycle_detail = {
                'cycle_length': f"{cycle['length']:.1f} days",
                'strength': f"{cycle['strength']:.3f}",
                'days_to_trough': f"{days_to_trough:.1f}",
                'days_to_peak': f"{days_to_peak:.1f}"
            }
            recommendation['details'].append(cycle_detail)
            
            # If within 10% of cycle length to trough, it's a buy signal
            trough_window = cycle['length'] * 0.1
            if days_to_trough <= trough_window:
                buy_signals += weight
                recommendation['reasoning'].append(
                    f"Approaching trough of {cycle['length']:.1f}-day cycle in {days_to_trough:.1f} days (strength: {cycle['strength']:.2f})."
                )
            
            # If within 10% of cycle length to peak, it's a sell signal
            peak_window = cycle['length'] * 0.1
            if days_to_peak <= peak_window:
                sell_signals += weight
                recommendation['reasoning'].append(
                    f"Approaching peak of {cycle['length']:.1f}-day cycle in {days_to_peak:.1f} days (strength: {cycle['strength']:.2f})."
                )
        
        # Normalize signals by total weight
        if total_weight > 0:
            buy_signals /= total_weight
            sell_signals /= total_weight
        
        # Adjust signals based on recent price movement (momentum)
        if recent_change > 0.02:  # 2% up recently
            sell_signals += 0.1
            recommendation['reasoning'].append(f"Recent upward price movement ({recent_change:.1%}) adds selling pressure.")
        elif recent_change < -0.02:  # 2% down recently
            buy_signals += 0.1
            recommendation['reasoning'].append(f"Recent downward price movement ({recent_change:.1%}) adds buying opportunity.")
        
        # Calculate overall recommendation
        overall_signal = buy_signals - sell_signals
        
        # Apply logic rules
        if overall_signal > 0.2:
            recommendation['action'] = 'BUY'
            recommendation['confidence'] = min(0.9, 0.5 + overall_signal)
        elif overall_signal < -0.2:
            recommendation['action'] = 'SELL'
            recommendation['confidence'] = min(0.9, 0.5 + abs(overall_signal))
        else:
            # If no strong signals, HOLD
            recommendation['action'] = 'HOLD'
            recommendation['confidence'] = 0.5 - abs(overall_signal)
            if not recommendation['reasoning']:
                recommendation['reasoning'].append("No strong cycle signals detected at this time.")
        
        # Add summary reasoning based on action
        if recommendation['action'] == 'BUY':
            recommendation['reasoning'].insert(0, "Multiple cycles suggest approaching price trough.")
        elif recommendation['action'] == 'SELL':
            recommendation['reasoning'].insert(0, "Multiple cycles suggest approaching price peak.")
        else:  # HOLD
            recommendation['reasoning'].insert(0, "Mixed or weak cycle signals suggest maintaining current position.")
        
        # Format confidence as percentage
        recommendation['confidence_pct'] = f"{recommendation['confidence']*100:.1f}%"
        
        return recommendation
    
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        # Return a safe default if there's an error
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'confidence_pct': '50.0%',
            'reasoning': ["An error occurred while generating the recommendation."]
        }
