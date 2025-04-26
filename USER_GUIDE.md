# Stock Market Signal Processing Web App - User Guide

This guide provides step-by-step instructions on how to use the Stock Market Signal Processing Web App effectively.

## Table of Contents
- [Getting Started](#getting-started)
- [Data Input Options](#data-input-options)
- [Understanding Your Results](#understanding-your-results)
- [Interpreting Recommendations](#interpreting-recommendations)
- [Exporting and Sharing](#exporting-and-sharing)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Troubleshooting](#troubleshooting)

## Getting Started

1. **Access the Application**
   - Open your web browser
   - Navigate to the application URL
   - You'll be presented with the home page featuring an upload form and ticker search

2. **Choose Your Data Source**
   - You can either:
     - Upload a CSV file with your historical stock data
     - Enter a stock ticker symbol to fetch live data

3. **Processing Time**
   - Analysis typically takes 5-15 seconds depending on the data size
   - You'll be automatically redirected to the results page when processing completes

## Data Input Options

### Option 1: Upload CSV File

1. **Prepare Your CSV File**
   - Your CSV file should contain at least two columns: date and price
   - Example format:
     ```
     date,price
     2023-01-01,150.25
     2023-01-02,152.30
     2023-01-03,149.75
     ```
   - Dates should be in YYYY-MM-DD format
   - Prices should be numerical values

2. **Upload Process**
   - Click the upload area or drag and drop your file
   - The filename will appear when successfully selected
   - Click "Analyze Stock Data" to begin processing

### Option 2: Enter Ticker Symbol

1. **Find Your Ticker Symbol**
   - Enter a valid stock ticker symbol (e.g., AAPL for Apple, MSFT for Microsoft)
   - The application will auto-suggest as you type

2. **Select Time Period**
   - Choose from available options:
     - 1 Year: Good for short-term cycles
     - 2 Years (default): Balanced for most analyses
     - 5 Years: Good for detecting longer-term cycles
     - 10 Years: Best for very long-term analysis
     - Max Available: All available historical data

3. **Submit for Analysis**
   - Click "Analyze Stock Data" to fetch and process the data

## Understanding Your Results

The results page is divided into several sections:

### 1. Summary Section

- **Stock Information**: Displays ticker symbol, date range, and analysis timestamp
- **Trading Recommendation**: Shows Buy, Hold, or Sell with confidence percentage
- **Reasoning**: Provides the rationale behind the recommendation

### 2. Time Series Chart

- **Blue Line**: Historical price data
- **Orange Line**: 7-day moving average
- **Red Line**: 30-day moving average
- **Interactive Features**:
  - Hover over points to see exact values
  - Zoom in/out with mouse wheel or selection
  - Pan by clicking and dragging
  - Reset view by double-clicking

### 3. Dominant Cycles

- **Cycle Cards**: Each card represents a significant cycle detected in your data
- **Period**: The length of the cycle in trading days
- **Strength**: How prominent this cycle is in the overall data
- **Current Position**: Where in the cycle we currently are
- **Cycle bars**: Visual representation of cycle strength

### 4. Frequency Analysis Chart

- **X-axis**: Cycle length in days (logarithmic scale)
- **Y-axis**: Amplitude (cycle strength)
- **Blue Line**: Power spectrum showing all detected cycles
- **Red Dots**: Dominant cycles
- **Text Labels**: Period length of top cycles

### 5. Forecast Chart

- **Blue Line**: Historical price data
- **Orange Dashed Line**: Projected price based on detected cycles
- **Vertical Line**: Divides historical data from forecast
- **Note**: Forecasts are estimations based on detected cycles and should not be considered guaranteed predictions

## Interpreting Recommendations

### Buy Recommendation
- **What it means**: The analysis suggests that price is likely to increase based on detected cycles
- **When you'll see it**: Typically when multiple cycles are at or near their bottom phase
- **Confidence levels**:
  - High (80-100%): Strong cycle alignment suggesting upward movement
  - Medium (60-79%): Moderate cycle alignment
  - Low (below 60%): Some signals present but with significant uncertainty

### Hold Recommendation
- **What it means**: The analysis suggests that no significant move is imminent, or signals are mixed
- **When you'll see it**: When cycles are in transitional phases or conflicting with each other
- **Confidence levels**:
  - High (80-100%): Strong evidence of sideways movement
  - Medium (60-79%): Balanced opposing signals
  - Low (below 60%): Unclear situation with low confidence in any direction

### Sell Recommendation
- **What it means**: The analysis suggests that price is likely to decrease based on detected cycles
- **When you'll see it**: Typically when multiple cycles are at or near their peak phase
- **Confidence levels**:
  - High (80-100%): Strong cycle alignment suggesting downward movement
  - Medium (60-79%): Moderate cycle alignment
  - Low (below 60%): Some signals present but with significant uncertainty

### Important Notes on Recommendations

- **Not Financial Advice**: These recommendations are based solely on cycle analysis and should not be considered financial advice
- **Complementary Tool**: Use these insights alongside other forms of analysis
- **Limitations**: Cycle analysis works better in some market conditions than others
- **Past Performance**: Remember that historical patterns do not guarantee future results

## Exporting and Sharing

### Generate PDF Report

1. Click the "Generate PDF Report" button
2. A PDF will be generated containing:
   - Summary information
   - Recommendation details
   - All charts and visualizations
   - Detected cycle information
   - Disclaimer and methodology notes

3. The PDF will automatically download to your device
4. PDF reports are designed for printing and sharing with others

### Download CSV Data

1. Click the "Download CSV" button
2. A CSV file will download containing:
   - Original price data
   - Processed data points
   - Detected cycle information
   - Forecast values

3. The CSV can be opened in any spreadsheet software for further analysis

## Frequently Asked Questions

### General Questions

**Q: How accurate is cycle analysis for predicting market movements?**
A: Cycle analysis can be very useful for identifying recurring patterns, but it's not a crystal ball. Markets are influenced by many factors beyond cycles, including news events, economic indicators, and sentiment changes. The accuracy tends to be higher when markets are in stable, trending conditions and lower during chaotic or news-driven periods.

**Q: How is the confidence rating calculated?**
A: Confidence ratings are calculated based on:
- The strength and clarity of detected cycles
- The alignment of multiple cycles
- The historical reliability of the detected cycle lengths
- The signal-to-noise ratio in the data

**Q: How far into the future can the forecast predict?**
A: The forecast is generally displayed for 30 trading days, but its reliability decreases as you look further into the future. The first 1-2 weeks are usually the most reliable part of any forecast.

**Q: Why don't I see any strong recommendations sometimes?**
A: Not all market conditions exhibit clear cyclical patterns. During periods of market transition or when influenced by external events, cycles may be weak or conflicting, resulting in low-confidence or hold recommendations.

### Technical Questions

**Q: What format should my CSV file be in?**
A: Your CSV file should have at least two columns: date and price. The date should be in YYYY-MM-DD format, and price should be numeric. Column headers should be included.

**Q: How much historical data is ideal for analysis?**
A: For most stocks, 1-2 years of daily data provides a good balance. Too little data (less than 6 months) may not reveal meaningful cycles, while too much data (over 5 years) might include different market regimes that could confuse the analysis.

**Q: Are cycles adjusted for weekends and holidays?**
A: Yes, the analysis works with trading days rather than calendar days, so weekends and market holidays are automatically accounted for.

**Q: What mathematical techniques are used for cycle detection?**
A: The application uses Fast Fourier Transform (FFT) to convert price data from the time domain to the frequency domain. Additional signal processing techniques are applied to improve cycle detection and reduce noise.

## Troubleshooting

### Common Issues

**Issue: My CSV file won't upload**
- Ensure your file is in CSV format (.csv extension)
- Check that your file has the required columns (date and price)
- Verify that your file is under the size limit (10MB)
- Make sure date format is YYYY-MM-DD

**Issue: No cycles detected**
- Try a different time period (some stocks show clearer cycles in different timeframes)
- The stock may not exhibit strong cyclical behavior
- Market conditions may be irregular or dominated by trend rather than cycles

**Issue: Error when entering ticker symbol**
- Verify that you're using the correct symbol
- Check that the stock is actively traded
- Some international stocks may not be available

**Issue: Charts not loading**
- Refresh the page
- Check your internet connection
- Try a different browser
- Clear your browser cache

### Getting Help

If you encounter persistent issues or have questions not covered in this guide:

1. Check the documentation for updates
2. Look for known issues in the project repository
3. Contact support with specific details about your issue