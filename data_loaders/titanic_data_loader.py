import polars as pl
from typing import Dict, Any


@data_loader
def load_titanic_data(**kwargs: Any) -> pl.DataFrame:
    """
    Load the public Titanic dataset and return it as a Polars DataFrame.
    
    Returns:
        pl.DataFrame: The Titanic dataset as a Polars DataFrame.
    """
    # Default URL for the Titanic dataset
    url = kwargs.get('url', 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
    
    # Load the data into a Polars DataFrame
    df = pl.read_csv(url)
    
    return df