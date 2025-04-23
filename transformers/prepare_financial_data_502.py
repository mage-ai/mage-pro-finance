import polars as pl
import numpy as np
from typing import Dict, Any


@transformer
def main( pl.DataFrame, **kwargs) -> pl.DataFrame:
    # Check if data is None
    if data is None:
        print("Warning: Input data is None. Returning empty DataFrame.")
        return pl.DataFrame()
    
    # Convert all column names to lowercase
    data = data.select([pl.col(col).alias(col.lower()) for col in data.columns])

    # Create time-based features
    data = data.with_columns([
        pl.col('date').dt.year().alias('year'),
        pl.col('date').dt.month().alias('month'),
        pl.col('date').dt.weekday().alias('dayofweek'),
        pl.col('date').dt.month().map_dict({
            1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
            7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }).alias('monthname'),
        pl.col('date').dt.weekday().map_dict({
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }).alias('dayname')
    ])
    
    # Calculate financial metrics
    # Trading range (High - Low)
    data = data.with_columns((pl.col('high') - pl.col('low')).alias('tradingrange'))
    
    # Percentage change from open to close
    data = data.with_columns(((pl.col('close') - pl.col('open')) / pl.col('open') * 100).alias('opentoclosechange'))
    
    # Daily returns (percentage change in closing price)
    data = data.with_columns(
        pl.col('close').pct_change().over('symbol') * 100
    ).rename({'changepercent': 'dailyreturn'})
    
    # Calculate 5-day and 20-day moving averages
    data = data.with_columns([
        pl.col('close').rolling_mean(window_size=5).over('symbol').alias('ma5'),
        pl.col('close').rolling_mean(window_size=20).over('symbol').alias('ma20')
    ])
    
    # Calculate volatility (standard deviation of returns over 20 days)
    data = data.with_columns(
        pl.col('dailyreturn').rolling_std(window_size=20).over('symbol').alias('volatility20d')
    )
    
    # Drop rows with missing values in essential columns
    data = data.drop_nulls(subset=['open', 'high', 'low', 'close', 'volume'])
    
    return data