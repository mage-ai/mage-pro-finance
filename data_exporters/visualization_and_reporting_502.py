import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any


@data_exporter
def main(market_analysis: pd.DataFrame, company_comparison: pd.DataFrame, 
         time_based_analysis: pd.DataFrame, volatility_analysis: pd.DataFrame, 
         volume_analysis: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Generate comprehensive visualizations and summary reports for stock market analysis.
    
    Args:
        market_analysis: DataFrame containing market analysis data
        company_comparison: DataFrame containing company comparison data
        time_based_analysis: DataFrame containing time-based analysis data
        volatility_analysis: DataFrame containing volatility analysis data
        volume_analysis: DataFrame containing volume analysis data
        
    Returns:
        Dictionary containing visualizations and summary reports
    """
    # Create a dictionary to store all visualizations and reports
    results = {}
    
    # 1. Interactive time series charts for price and volume
    companies = company_comparison['symbol'].unique().tolist()
    price_volume_figs = {}
    
    for company in companies:
        company_data = time_based_analysis[time_based_analysis['symbol'] == company]
        
        # Create subplot with 2 y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add price line
        fig.add_trace(
            go.Scatter(x=company_data['date'], y=company_data['close'], name=f"{company} Price"),
            secondary_y=False,
        )
        
        # Add volume bars
        fig.add_trace(
            go.Bar(x=company_data['date'], y=company_data['volume'], name=f"{company} Volume"),
            secondary_y=True,
        )
        
        # Set titles
        fig.update_layout(
            title_text=f"{company} Price and Volume Over Time",
            xaxis_title="Date",
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="Volume", secondary_y=True)
        
        price_volume_figs[company] = fig
    
    results['price_volume_charts'] = price_volume_figs
    
    # 2. Correlation heatmap
    correlation_data = company_comparison.pivot(index='date', columns='symbol', values='close')
    corr_matrix = correlation_data.corr()
    
    # Create heatmap using Plotly
    corr_fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title='Correlation Heatmap of Stock Prices'
    )
    
    results['correlation_heatmap'] = corr_fig
    
    # 3. Performance comparison heatmap
    performance_metrics = company_comparison.pivot(index='symbol', columns='metric', values='value')
    
    # Create performance heatmap
    perf_fig = px.imshow(
        performance_metrics,
        text_auto=True,
        color_continuous_scale='Viridis',
        title='Performance Metrics Comparison'
    )
    
    results['performance_heatmap'] = perf_fig
    
    # 4. Volatility comparison
    volatility_fig = px.bar(
        volatility_analysis,
        x='symbol',
        y='volatility',
        color='symbol',
        title='Volatility Comparison Across Companies'
    )
    
    results['volatility_chart'] = volatility_fig
    
    # 5. Volume analysis over time
    volume_fig = px.line(
        volume_analysis,
        x='date',
        y='volume',
        color='symbol',
        title='Trading Volume Over Time'
    )
    
    results['volume_trend_chart'] = volume_fig
    
    # 6. Summary tables with key performance metrics
    summary_table = company_comparison.pivot(index='symbol', columns='metric', values='value')
    
    # Add market average as a reference
    market_avg = summary_table.mean()
    summary_table.loc['Market Average'] = market_avg
    
    results['summary_table'] = summary_table
    
    # 7. Risk vs Return scatter plot
    risk_return_fig = px.scatter(
        volatility_analysis,
        x='volatility',
        y='return',
        color='symbol',
        size='sharpe_ratio',
        hover_data=['beta', 'max_drawdown'],
        title='Risk vs Return Analysis'
    )
    
    results['risk_return_chart'] = risk_return_fig
    
    return results