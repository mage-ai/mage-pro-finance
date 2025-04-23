import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple


@transformer
def main( pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Perform volatility and risk analysis on financial data.
    
    Args:
         DataFrame containing financial data with columns for date, ticker, and close prices
        
    Returns:
        Dictionary containing volatility metrics, risk analysis, and periods of high volatility
    """
    # Extract parameters from kwargs or use defaults
    risk_free_rate = kwargs.get('risk_free_rate', 0.02)  # Annual risk-free rate
    market_index = kwargs.get('market_index', 'SPY')  # Default market index
    volatility_threshold = kwargs.get('volatility_threshold', 0.02)  # 2% daily change threshold
    
    # Ensure data is properly formatted
    if 'date' not in data.columns:
        raise ValueError("Data must contain a 'date' column")
    if 'ticker' not in data.columns:
        raise ValueError("Data must contain a 'ticker' column")
    if 'close' not in data.columns:
        raise ValueError("Data must contain a 'close' column")
    
    # Convert date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])
    
    # Pivot data to have tickers as columns and dates as index
    pivot_data = data.pivot(index='date', columns='ticker', values='close')
    
    # Calculate daily returns
    daily_returns = pivot_data.pct_change().dropna()
    
    # Get list of all tickers excluding the market index
    all_tickers = [ticker for ticker in daily_returns.columns if ticker != market_index]
    
    # Volatility metrics
    volatility_metrics = {}
    for ticker in daily_returns.columns:
        volatility_metrics[ticker] = {
            'annualized_volatility': daily_returns[ticker].std() * np.sqrt(252),
            'max_drawdown': calculate_max_drawdown(pivot_data[ticker]),
        }
        
        # Calculate Sharpe ratio if risk-free rate is available
        if risk_free_rate is not None:
            daily_risk_free = risk_free_rate / 252
            excess_return = daily_returns[ticker] - daily_risk_free
            volatility_metrics[ticker]['sharpe_ratio'] = (
                excess_return.mean() / excess_return.std() * np.sqrt(252)
            )
    
    # Calculate beta for each stock relative to market index if available
    beta_values = {}
    if market_index in daily_returns.columns:
        market_returns = daily_returns[market_index]
        for ticker in all_tickers:
            stock_returns = daily_returns[ticker]
            covariance = stock_returns.cov(market_returns)
            market_variance = market_returns.var()
            beta = covariance / market_variance
            beta_values[ticker] = beta
    
    # Identify periods of high volatility
    high_volatility_periods = {}
    rolling_volatility = daily_returns.rolling(window=21).std() * np.sqrt(252)  # 21-day rolling annualized volatility
    
    for ticker in daily_returns.columns:
        # Find dates where volatility exceeds the threshold
        high_vol_dates = rolling_volatility[rolling_volatility[ticker] > volatility_threshold].index
        
        if len(high_vol_dates) > 0:
            # Group consecutive dates into periods
            high_vol_periods = []
            current_period_start = high_vol_dates[0]
            current_period_end = high_vol_dates[0]
            
            for i in range(1, len(high_vol_dates)):
                if (high_vol_dates[i] - high_vol_dates[i-1]).days <= 7:  # Consider consecutive if within 7 days
                    current_period_end = high_vol_dates[i]
                else:
                    high_vol_periods.append((current_period_start, current_period_end))
                    current_period_start = high_vol_dates[i]
                    current_period_end = high_vol_dates[i]
            
            # Add the last period
            high_vol_periods.append((current_period_start, current_period_end))
            high_volatility_periods[ticker] = high_vol_periods
    
    # Compare risk-adjusted returns across companies
    risk_adjusted_comparison = {}
    for ticker in all_tickers:
        risk_adjusted_comparison[ticker] = {
            'annualized_return': daily_returns[ticker].mean() * 252,
            'annualized_volatility': volatility_metrics[ticker]['annualized_volatility'],
            'sharpe_ratio': volatility_metrics[ticker].get('sharpe_ratio', None),
            'max_drawdown': volatility_metrics[ticker]['max_drawdown'],
            'beta': beta_values.get(ticker, None)
        }
    
    # Return comprehensive volatility analysis
    return {
        'volatility_metrics': volatility_metrics,
        'beta_values': beta_values,
        'high_volatility_periods': high_volatility_periods,
        'risk_adjusted_comparison': risk_adjusted_comparison,
        'rolling_volatility': rolling_volatility
    }


def calculate_max_drawdown(price_series: pd.Series) -> float:
    """
    Calculate the maximum drawdown for a price series.
    
    Args:
        price_series: Series of prices
        
    Returns:
        Maximum drawdown as a decimal (not percentage)
    """
    # Calculate the cumulative maximum
    rolling_max = price_series.cummax()
    
    # Calculate drawdown
    drawdown = (price_series - rolling_max) / rolling_max
    
    # Return the minimum drawdown (maximum loss)
    return drawdown.min()