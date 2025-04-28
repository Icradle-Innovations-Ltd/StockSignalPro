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
        
        # If no dominant cycles, return HOLD with clear explanation
        if not dominant_cycles:
            recommendation['reasoning'].append("No significant market cycles detected. This suggests the market lacks clear cyclical patterns, making it difficult to predict future price movements.")
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
                    f"A {cycle['length']:.1f}-day market cycle is nearing its lowest point (trough) in {days_to_trough:.1f} days. "
                    f"This cycle has a strength rating of {cycle['strength']:.2f}, indicating a potential buying opportunity "
                    f"as prices typically rise after reaching this point in the cycle."
                )
            
            # If within 10% of cycle length to peak, it's a sell signal
            peak_window = cycle['length'] * 0.1
            if days_to_peak <= peak_window:
                sell_signals += weight
                recommendation['reasoning'].append(
                    f"A {cycle['length']:.1f}-day market cycle is approaching its highest point (peak) in {days_to_peak:.1f} days. "
                    f"With a cycle strength of {cycle['strength']:.2f}, this suggests a potential selling opportunity "
                    f"as prices typically decline after reaching this peak."
                )
        
        # Normalize signals by total weight
        if total_weight > 0:
            buy_signals /= total_weight
            sell_signals /= total_weight
        
        # Adjust signals based on recent price movement (momentum)
        if recent_change > 0.02:  # 2% up recently
            sell_signals += 0.1
            recommendation['reasoning'].append(
                f"The price has increased by {recent_change:.1%} recently, suggesting potential profit-taking opportunity. "
                "This upward momentum might indicate a short-term peak forming."
            )
        elif recent_change < -0.02:  # 2% down recently
            buy_signals += 0.1
            recommendation['reasoning'].append(
                f"The price has decreased by {abs(recent_change):.1%} recently, presenting a potential value buying opportunity. "
                "This downward movement might indicate a short-term bottom forming."
            )
        
        # Calculate overall recommendation
        overall_signal = buy_signals - sell_signals
        
        # Apply logic rules with detailed explanations
        if overall_signal > 0.2:
            recommendation['action'] = 'BUY'
            recommendation['confidence'] = min(0.9, 0.5 + overall_signal)
        elif overall_signal < -0.2:
            recommendation['action'] = 'SELL'
            recommendation['confidence'] = min(0.9, 0.5 + abs(overall_signal))
        else:
            recommendation['action'] = 'HOLD'
            recommendation['confidence'] = 0.5 - abs(overall_signal)
            if not recommendation['reasoning']:
                recommendation['reasoning'].append(
                    "Current market cycles show balanced or unclear signals. No strong buying or selling pressure detected. "
                    "It's advisable to maintain current positions until clearer patterns emerge."
                )
        
        # Add comprehensive summary reasoning based on action
        if recommendation['action'] == 'BUY':
            recommendation['reasoning'].insert(0, 
                "Multiple market cycles are converging towards their low points, suggesting a strong buying opportunity. "
                "The alignment of these cycles, combined with their respective strengths, indicates a higher probability "
                "of price appreciation in the near future."
            )
        elif recommendation['action'] == 'SELL':
            recommendation['reasoning'].insert(0, 
                "Multiple market cycles are approaching their peak values, indicating a strong selling opportunity. "
                "The convergence of these cycle peaks, weighted by their individual strengths, suggests an increased "
                "likelihood of price decline in the near term."
            )
        else:  # HOLD
            recommendation['reasoning'].insert(0, 
                "Current market cycles show mixed or weak signals without clear directional bias. "
                "The combination of cycle positions and their strengths suggests maintaining current positions "
                "until more definitive patterns emerge."
            )
        
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
