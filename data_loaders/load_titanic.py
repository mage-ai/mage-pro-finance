import io
import pandas as pd
import requests
from pandas import DataFrame

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(**kwargs) -> DataFrame:
    """
    Template for loading data from API
    """
    country = kwargs.get('country')
    url = f'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv?raw=True&country={country}'

    return pd.read_csv(url).iloc[:10]


@test
def test_output(df) -> None:
    """
    Template code for testing the output of the block.
    """
    assert 1 > 1000, 'The output is undefined'