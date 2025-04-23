import io
import polars as pl
import pandas as pd
from typing import Any


@transformer
def transform_csv_content_to_dataframe(df: Any, **kwargs: Any) -> pl.DataFrame:
    """
    Transform CSV content from input dataframe into a single polars dataframe.
    
    Args:
        df: Input dataframe containing a 'content' column with CSV file content
        **kwargs: Additional keyword arguments
        
    Returns:
        Concatenated polars dataframe with all CSV content
    """
    # Convert pandas DataFrame to polars if needed
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
    
    # List to store individual dataframes
    dataframes = []
    
    # Process each row in the input dataframe
    for row in df.iter_rows(named=True):
        # Get CSV content from the row
        csv_content = row['content']
        
        # Convert CSV content to a polars dataframe
        if isinstance(csv_content, bytes):
            # Either decode bytes to string
            csv_content = csv_content.decode('utf-8')
            csv_io = io.StringIO(csv_content)
            # Or use BytesIO directly
            # csv_io = io.BytesIO(csv_content)
        else:
            csv_io = io.StringIO(csv_content)
            
        try:
            # Add truncate_ragged_lines=True to handle inconsistent column counts
            row_df = pl.read_csv(csv_io, truncate_ragged_lines=True)
            
            # Add to list of dataframes
            dataframes.append(row_df)
        except Exception as e:
            # Optional: Add error handling to log problematic CSV data
            print(f"Error processing CSV content: {e}")
            continue
    
    # Concatenate all dataframes
    if dataframes:
        result_df = pl.concat(dataframes)
        return result_df
    else:
        # Return empty dataframe if no data
        return pl.DataFrame()


@test
def validate_row_count(df):
    assert len(df) >= 17_000, f'Expected 17,000 rows, got {len(df)}'


@test
def validate_column_types(df):
    # Check if dataframe has columns
    assert len(df.columns) > 0, "DataFrame has no columns"
    
    # Get schema information
    schema = df.schema
    
    # Check specific column types if they exist
    for col_name, dtype in schema.items():
        # Verify column types are appropriate (can be customized based on expected data)
        assert dtype in [pl.Float64, pl.Int64, pl.Utf8, pl.Boolean, pl.Date, pl.Datetime], \
            f"Column '{col_name}' has unexpected data type: {dtype}"