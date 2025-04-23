import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
from plotly.subplots import make_subplots 


@transformer
def analyze_market_trends(market_data, **kwargs) -> Dict[str, Any]:
    market_data = market_data.to_pandas()
    
    # Calculate daily returns if not already present
    if 'daily_return' not in market_data.columns:
        market_data['daily_return'] = market_data.groupby('symbol')['close'].pct_change() * 100
    
    # Create a market index by averaging prices across all companies
    market_index = market_data.groupby('date')['close'].mean().reset_index()
    market_index.columns = ['date', 'market_index']
    
    # Calculate market daily returns
    market_index['market_return'] = market_index['market_index'].pct_change() * 100
    
    # Calculate summary statistics for key metrics
    summary_stats = {
        'daily_returns': market_data.groupby('date')['daily_return'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index(),
        'volume': market_data.groupby('date')['volume'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index(),
        'price': market_data.groupby('date')['close'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
    }
    
    # Calculate rolling market volatility (20-day standard deviation of returns)
    market_volatility = market_index.copy()
    market_volatility['rolling_volatility'] = market_volatility['market_return'].rolling(window=20).std()
    
    # Calculate average daily trading volume over time
    avg_daily_volume = market_data.groupby('date')['volume'].mean().reset_index()
    avg_daily_volume.columns = ['date', 'avg_volume']
    
    # Identify market trends
    # Calculate 50-day and 200-day moving averages for the market index
    market_trends = market_index.copy()
    market_trends['ma_50'] = market_trends['market_index'].rolling(window=50).mean()
    market_trends['ma_200'] = market_trends['market_index'].rolling(window=200).mean()
    
    # Create plots using plotly
    # Market index plot with moving averages
    fig_market = go.Figure()
    fig_market.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['market_index'], mode='lines', name='Market Index'))
    fig_market.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['ma_50'], mode='lines', name='50-day MA', line=dict(dash='dash')))
    fig_market.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['ma_200'], mode='lines', name='200-day MA', line=dict(dash='dot')))
    fig_market.update_layout(title='Market Index with Moving Averages', xaxis_title='Date', yaxis_title='Index Value')
    
    # Volume plot
    fig_volume = px.line(avg_daily_volume, x='date', y='avg_volume', title='Average Daily Trading Volume')
    
    # Create a combined figure with subplots
    fig = go.Figure()
    fig = make_subplots(rows=3, cols=1, subplot_titles=('Market Index with Moving Averages', 
                                                        'Average Daily Trading Volume'))

    # Market index plot with moving averages (first subplot)
    fig.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['market_index'], 
                                mode='lines', name='Market Index'), row=1, col=1)
    fig.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['ma_50'], 
                                mode='lines', name='50-day MA', line=dict(dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=market_trends['date'], y=market_trends['ma_200'], 
                                mode='lines', name='200-day MA', line=dict(dash='dot')), row=1, col=1)

    # Volume plot (2nd subplot)
    fig.add_trace(go.Scatter(x=avg_daily_volume['date'], y=avg_daily_volume['avg_volume'],
                                mode='lines', name='Avg Volume'), row=2, col=1)

    fig.update_layout(height=900, title_text="Market Analysis Dashboard")

    return fig.to_dict()