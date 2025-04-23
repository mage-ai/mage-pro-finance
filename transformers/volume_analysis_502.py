import numpy as np
import pandas as pd
from typing import Dict, Any


@transformer
def main(financial_ pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Analyze trading volume patterns, identify unusual volume spikes, and calculate VWAP.
    
    Args:
        financial_data: DataFrame containing stock price and volume data
        
    Returns:
        Dictionary containing volume analysis results
    """
    # Make a copy to avoid modifying the original data
    df = financial_data.copy()
    
    # Ensure we have the necessary columns
    required_columns = ['date', 'symbol', 'volume', 'close', 'open', 'high', 'low']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in input data")
    
    # Group by symbol to analyze each company separately
    symbols = df['symbol'].unique()
    results = {}
    
    for symbol in symbols:
        symbol_data = df[df['symbol'] == symbol].sort_values('date')
        
        # Skip if not enough data
        if len(symbol_data) < 2:
            continue
            
        # Calculate daily price change
        symbol_data['price_change'] = symbol_data['close'].pct_change()
        
        # Calculate daily volume change
        symbol_data['volume_change'] = symbol_data['volume'].pct_change()
        
        # Calculate volume-weighted average price (VWAP)
        symbol_data['vwap'] = (symbol_data['volume'] * 
                              (symbol_data['high'] + symbol_data['low'] + symbol_data['close']) / 3).cumsum() / \
                              symbol_data['volume'].cumsum()
        
        # Calculate rolling average volume (20-day)
        symbol_data['avg_volume_20d'] = symbol_data['volume'].rolling(window=20, min_periods=1).mean()
        
        # Identify unusual volume spikes (volume > 2x 20-day average)
        symbol_data['volume_spike'] = symbol_data['volume'] > 2 * symbol_data['avg_volume_20d']
        
        # Calculate correlation between volume and price changes
        volume_price_corr = symbol_data['volume_change'].corr(symbol_data['price_change'])
        
        # Analyze volume spikes and their impact on price
        volume_spikes = symbol_data[symbol_data['volume_spike']]
        avg_price_change_on_spikes = volume_spikes['price_change'].mean() if not volume_spikes.empty else np.nan
        
        # Compare monthly trading activity
        symbol_data['month'] = pd.to_datetime(symbol_data['date']).dt.to_period('M')
        monthly_volume = symbol_data.groupby('month')['volume'].sum()
        monthly_vwap = symbol_data.groupby('month').apply(
            lambda x: (x['volume'] * x['close']).sum() / x['volume'].sum() if x['volume'].sum() > 0 else np.nan
        )
        
        # Store results for this symbol
        results[symbol] = {
            'data': symbol_data,
            'volume_price_correlation': volume_price_corr,
            'volume_spikes_count': volume_spikes.shape[0],
            'avg_price_change_on_spikes': avg_price_change_on_spikes,
            'monthly_volume': monthly_volume,
            'monthly_vwap': monthly_vwap,
            'max_volume_day': symbol_data.loc[symbol_data['volume'].idxmax()],
            'min_volume_day': symbol_data.loc[symbol_data['volume'].idxmin()]
        }
    
    # Calculate cross-company volume comparison
    if len(symbols) > 1:
        # Normalize volumes across companies for comparison
        volume_by_company = {}
        for symbol in symbols:
            if symbol in results:
                symbol_data = results[symbol]['data']
                # Normalize to percentage of average volume
                avg_volume = symbol_data['volume'].mean()
                volume_by_company[symbol] = symbol_data.set_index('date')['volume'] / avg_volume
        
        # Create a DataFrame with normalized volumes for all companies
        if volume_by_company:
            normalized_volumes = pd.DataFrame(volume_by_company)
            results['cross_company_volume_correlation'] = normalized_volumes.corr()
    
    return results