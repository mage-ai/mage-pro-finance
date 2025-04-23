import pandas as pd
import polars as pl
import plotly.express as px
from typing import Dict, Any


@transformer
def calculate_performance_metrics(data, **kwargs) -> Dict[str, Any]:
    """
    Calculate performance metrics for stocks and create a risk vs return visualization.
    
    Returns:
        Dict[str, Any]: A plotly figure as a dictionary
    """
    # Check if data is a polars DataFrame and convert to pandas if needed
    if isinstance(data, pl.DataFrame):
        # Convert to pandas for compatibility
        data = data.to_pandas()
    
    # Initialize metrics dictionary
    metrics = {}
    subset = ['daily_return']
    
    # Check if data contains multiple stocks
    if 'symbol' in data.columns:
        # Group by ticker
        for ticker, df in data.groupby('symbol'):
            # Skip if not enough data
            if len(df) < 2:
                continue
                
            # Calculate daily returns if not already present
            if 'daily_return' not in df.columns:
                df['daily_return'] = df['close'].pct_change()
            
            # Drop NaN values
            df = df.dropna(subset=subset)
            
            # Skip if not enough data after dropping NaNs
            if len(df) < 2:
                continue
                
            # Calculate metrics
            avg_return = df['daily_return'].mean()
            volatility = df['daily_return'].std()
            total_return = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
            
            # Calculate Sharpe Ratio safely
            sharpe_ratio = avg_return / volatility if volatility != 0 else 0
            
            # Store metrics
            metrics[ticker] = {
                'Ticker': ticker,
                'Average Daily Return': avg_return,
                'Volatility': volatility,
                'Total Return': total_return,
                'Sharpe Ratio': sharpe_ratio
            }
    else:
        # Assume it's a single stock's data without ticker information
        if 'close' in data.columns:
            if 'daily_return' not in data.columns:
                data['daily_return'] = data['close'].pct_change()
            
            # Drop NaN values
            data = data.dropna(subset=subset)
            
            # Skip if not enough data
            if len(data) >= 2:
                # Calculate metrics
                avg_return = data['daily_return'].mean()
                volatility = data['daily_return'].std()
                total_return = (data['close'].iloc[-1] / data['close'].iloc[0]) - 1
                
                # Calculate Sharpe Ratio safely
                sharpe_ratio = avg_return / volatility if volatility != 0 else 0
                
                # Store metrics
                metrics['Stock'] = {
                    'Ticker': 'Stock',
                    'Average Daily Return': avg_return,
                    'Volatility': volatility,
                    'Total Return': total_return,
                    'Sharpe Ratio': sharpe_ratio
                }
    
    # Check if metrics dictionary is empty
    if not metrics:
        return px.scatter(title="No valid data for visualization").to_dict()
        
    performance_df = pd.DataFrame.from_dict(metrics, orient='index')
    
    # Replace any remaining NaN values with 0 for plotting
    performance_df = performance_df.fillna(0)
    
    # Create a new column for bubble size that ensures positive values
    performance_df['Bubble Size'] = performance_df['Sharpe Ratio'].abs() + 0.1  # Add 0.1 to ensure positive values
    
    # Create plotly figure
    fig = px.scatter(
        performance_df, 
        x='Volatility', 
        y='Total Return',
        size='Bubble Size',  # Use the new positive column for size
        color='Sharpe Ratio',  # Keep original Sharpe Ratio for color
        hover_name=performance_df.index,
        text=performance_df.index,
        title='Risk vs. Return Analysis',
        labels={
            'Volatility': 'Risk (Volatility)',
            'Total Return': 'Total Return (%)',
            'Sharpe Ratio': 'Risk-Adjusted Return'
        },
        color_continuous_scale='viridis'
    )
    
    # Add annotations for best and worst performers if we have multiple stocks
    if len(performance_df) > 1:
        best_performer = performance_df['Total Return'].idxmax()
        worst_performer = performance_df['Total Return'].idxmin()
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
        coloraxis_colorbar=dict(title="Sharpe Ratio"),
        hovermode='closest'
    )
    
    # Convert to dictionary for return
    return fig.to_dict()