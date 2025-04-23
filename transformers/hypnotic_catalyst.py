import pandas as pd
from typing import Any, Dict


@transformer
def lowercase_column_names(**kwargs: Dict[str, Any]) -> pd.DataFrame:
    """
    Transforms all column names in a pandas DataFrame to lowercase.
    
    Args:
        **kwargs: Keyword arguments that may contain a DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame with lowercase column names.
    """
    # Get DataFrame from kwargs
    df = kwargs.get('df')
    
    if df is None:
        raise ValueError("No DataFrame provided in kwargs. Please provide a DataFrame using the 'df' key.")
    
    # Convert column names to lowercase
    df.columns = df.columns.str.lower()
    
    return df