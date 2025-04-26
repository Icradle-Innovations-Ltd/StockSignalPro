import json
import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())


class Analysis(db.Model):
    """Model for storing stock analysis data."""
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ticker = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_type = db.Column(db.String(10))  # 'file' or 'api'
    filename = db.Column(db.String(255), nullable=True)
    data = db.Column(JSON)
    recommendation = db.Column(JSON)
    dominant_cycles = db.Column(JSON)
    time_series_plot = db.Column(JSON)
    frequency_plot = db.Column(JSON)
    forecast_plot = db.Column(JSON)
    # Link to Portfolio (optional)
    portfolio_id = db.Column(db.String(36), db.ForeignKey('portfolio.id'), nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'created_at': self.created_at.isoformat(),
            'source_type': self.source_type,
            'filename': self.filename,
            'recommendation': self.recommendation,
            'dominant_cycles': self.dominant_cycles,
            'time_series_plot': self.time_series_plot,
            'frequency_plot': self.frequency_plot,
            'forecast_plot': self.forecast_plot,
            'portfolio_id': self.portfolio_id
        }


class MarketSentiment(db.Model):
    """Model for storing market sentiment data."""
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ticker = db.Column(db.String(10), nullable=True)  # Optional specific ticker
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bullish_score = db.Column(db.Float)
    bearish_score = db.Column(db.Float)
    neutral_score = db.Column(db.Float)
    mood = db.Column(db.String(20))  # 'bullish', 'bearish', or 'neutral'
    mood_value = db.Column(db.Float)  # Numeric value between 0-100
    sentiment_gauge = db.Column(JSON)  # Plotly chart JSON
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'created_at': self.created_at.isoformat(),
            'bullish_score': self.bullish_score,
            'bearish_score': self.bearish_score,
            'neutral_score': self.neutral_score,
            'mood': self.mood,
            'mood_value': self.mood_value,
            'sentiment_gauge': self.sentiment_gauge
        }


class Portfolio(db.Model):
    """Model for storing portfolio data with multiple stocks."""
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Store stock tickers as a JSON list
    stocks = db.Column(JSON)
    # Store allocation percentages as a JSON dictionary (ticker: percentage)
    allocations = db.Column(JSON)
    # Store correlation matrix as JSON
    correlation_matrix = db.Column(JSON)
    # Store portfolio visualization as JSON (Plotly figure)
    portfolio_plot = db.Column(JSON)
    # Store cycle analysis results
    cycle_analysis = db.Column(JSON)
    # Relationship with Analysis
    analyses = db.relationship('Analysis', backref='portfolio', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'stocks': self.stocks,
            'allocations': self.allocations,
            'correlation_matrix': self.correlation_matrix,
            'portfolio_plot': self.portfolio_plot,
            'cycle_analysis': self.cycle_analysis
        }