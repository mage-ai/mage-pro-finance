import os
import polars as pl
from typing import Dict, Any, List, Optional, Union


@data_loader
def main(dfs, **kwargs) -> pl.DataFrame:
    df = dfs['ethereal_crucible']

    if isinstance(df, list) and len(df) > 0:
        df = df[0]

    symbol = kwargs.get('symbol')
    
    if symbol:
        symbol = symbol.upper()
        df = df.filter(pl.col('symbol') == symbol)
    
    # Parse date column as datetime
    df = df.with_columns(pl.col('date').str.strptime(pl.Datetime, format='%Y-%m-%d'))

    print(f"Successfully loaded stock data with {df.shape[0]} rows and {df.shape[1]} columns")
    
    return df