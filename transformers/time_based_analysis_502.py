import numpy as np
import pandas as pd
from typing import Dict, Any


@transformer
def main( pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Perform time-based analysis on financial data to identify patterns and seasonality.
    
    Args:
        data: A pandas DataFrame containing financial data with a datetime index
        
    Returns:
        A dictionary containing various time-based analyses
    """
    # Ensure the index is datetime
    if not isinstance(data.index, pd.DatetimeIndex):
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')
        else:
            raise ValueError("DataFrame must have a datetime index or a 'Date' column")
    
    # Make a copy to avoid modifying the original data
    df = data.copy()
    
    # Add time-based features
    df['Year'] = df.index.year
    df['Month'] = df.index.month
    df['Day'] = df.index.day
    df['DayOfWeek'] = df.index.dayofweek
    df['Quarter'] = df.index.quarter
    
    # Initialize results dictionary
    results = {}
    
    # Analyze performance by different time periods
    # Yearly analysis
    yearly_returns = df.groupby('Year')['Close'].apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    yearly_volatility = df.groupby('Year')['Close'].apply(lambda x: x.pct_change().std() * np.sqrt(252) * 100)
    results['yearly_analysis'] = pd.DataFrame({
        'Return (%)': yearly_returns,
        'Volatility (%)': yearly_volatility
    })
    
    # Monthly analysis
    monthly_returns = df.groupby(['Year', 'Month'])['Close'].apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
    monthly_volatility = df.groupby(['Year', 'Month'])['Close'].apply(lambda x: x.pct_change().std() * np.sqrt(21) * 100)
    results['monthly_analysis'] = pd.DataFrame({
        'Return (%)': monthly_returns,
        'Volatility (%)': monthly_volatility
    })
    
    # Day of week analysis
    dow_returns = df.groupby('DayOfWeek')['Close'].pct_change().mean() * 100
    dow_volatility = df.groupby('DayOfWeek')['Close'].pct_change().std() * 100
    results['day_of_week_analysis'] = pd.DataFrame({
        'Avg Return (%)': dow_returns,
        'Volatility (%)': dow_volatility
    })
    
    # Calculate rolling metrics
    # Rolling average (20-day, 50-day, 200-day)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Rolling volatility (20-day)
    df['Volatility_20d'] = df['Close'].pct_change().rolling(window=20).std() * np.sqrt(252) * 100
    
    # Detect crossovers (potential trading signals)
    df['Golden_Cross'] = (df['MA50'] > df['MA200']) & (df['MA50'].shift(1) <= df['MA200'].shift(1))
    df['Death_Cross'] = (df['MA50'] < df['MA200']) & (df['MA50'].shift(1) >= df['MA200'].shift(1))
    
    # Identify seasonal patterns
    monthly_avg_returns = df.groupby('Month')['Close'].pct_change().mean() * 100
    results['seasonal_monthly_returns'] = monthly_avg_returns
    
    # Identify anomalies (returns exceeding 2 standard deviations)
    daily_returns = df['Close'].pct_change()
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    df['Anomaly'] = (daily_returns > (mean_return + 2 * std_return)) | (daily_returns < (mean_return - 2 * std_return))
    results['anomalies'] = df[df['Anomaly']].copy()
    
    # Add the processed dataframe to results
    results['processed_data'] = df
    
    return results