import pandas as pd
import io
from typing import Any


@transformer
def transform_stock_data(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Transform the input dataframe to create a new dataframe with stock price information.
    
    Args:
        df: Input pandas DataFrame from upstream block
        **kwargs: Additional keyword arguments
        
    Returns:
        pd.DataFrame: A new pandas DataFrame containing stock price data
    """
    # First, let's check what columns are actually available
    print(f"Available columns: {df.columns.tolist()}")
    
    # Check if the DataFrame is empty
    if df.empty:
        print("The input DataFrame is empty")
        return pd.DataFrame()
    
    # Check if 'content' column exists (from SFTP CSV files)
    if 'content' in df.columns:
        # Parse CSV content from the 'content' column
        try:
            # Create a list to store individual dataframes
            parsed_dfs = []
            
            # Process each row in the content column
            for idx, content in enumerate(df['content']):
                try:
                    # Check if content is bytes and convert to string if needed
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    elif content is None:
                        print(f"Skipping index {idx}: Content is None")
                        continue
                    
                    # Parse CSV content into a DataFrame
                    parsed_df = pd.read_csv(io.StringIO(content))
                    
                    # Add source information if available
                    if 'filename' in df.columns:
                        parsed_df['source_file'] = df.loc[idx, 'filename']
                    
                    parsed_dfs.append(parsed_df)
                except Exception as e:
                    print(f"Error parsing CSV content at index {idx}: {e}")
            
            # Combine all parsed DataFrames
            if parsed_dfs:
                stock_price_df = pd.concat(parsed_dfs, ignore_index=True)
            else:
                print("No CSV content could be parsed")
                stock_price_df = pd.DataFrame()
                
        except Exception as e:
            print(f"Error processing 'content' column: {e}")
            stock_price_df = df.copy()
    else:
        # Try to extract stock price data using available columns
                try:
                    # Create a new DataFrame with proper column headers
                    if len(df) > 0:
                        # Check if the first row looks like headers
                        first_row = df.iloc[0]
                        if any(str(val).lower() in ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'] for val in first_row):
                            # Use first row as headers
                            headers = [str(val).lower() for val in first_row]
                            stock_price_df = pd.DataFrame(df.iloc[1:].values, columns=headers)
                            
                            # Map standard column names
                            column_mapping = {}
                            required_cols = ["date", "symbol", "open", "high", "low", "close", "volume"]
                            
                            for col in stock_price_df.columns:
                                if 'date' in col.lower() or 'time' in col.lower():
                                    column_mapping[col] = 'date'
                                elif 'symbol' in col.lower() or 'ticker' in col.lower():
                                    column_mapping[col] = 'symbol'
                                elif 'open' in col.lower():
                                    column_mapping[col] = 'open'
                                elif 'high' in col.lower():
                                    column_mapping[col] = 'high'
                                elif 'low' in col.lower():
                                    column_mapping[col] = 'low'
                                elif 'close' in col.lower() or 'last' in col.lower():
                                    column_mapping[col] = 'close'
                                elif 'volume' in col.lower() or 'vol' in col.lower():
                                    column_mapping[col] = 'volume'
                            
                            stock_price_df = stock_price_df.rename(columns=column_mapping)
                            
                            # Select only the required columns if they exist
                            available_cols = [col for col in required_cols if col in stock_price_df.columns]
                            if available_cols:
                                stock_price_df = stock_price_df[available_cols]
                        else:
                            # Use existing column names
                            stock_price_df = df.copy()
                    else:
                        stock_price_df = df.copy()
                except Exception as e:
                    print(f"Error processing DataFrame: {e}")
                    # Return the original DataFrame if there's an error
                    stock_price_df = df.copy()
            
            return stock_price_df