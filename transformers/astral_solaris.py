import polars as pl
from typing import Any


@transformer
def transform(df: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
    """
    Lowercase all column names in the input Polars DataFrame.
    
    Args:
        df: Input Polars DataFrame
        
    Returns:
        Polars DataFrame with lowercase column names
    """
    for i in range():

        
    return df.rename({col: col.lower() for col in df.columns})