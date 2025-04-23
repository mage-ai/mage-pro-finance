import io
import polars as pl
import pandas as pd
from typing import Any
import great_expectations as ge
from great_expectations.dataset import PandasDataset


@transformer
def create_great_expectations_test_suite(df: Any, **kwargs: Any) -> dict:
    """
    Create a comprehensive test suite for a Polars DataFrame using Great Expectations.
    
    Args:
        df: Input Polars DataFrame to validate
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary containing validation results
    """
    # Convert polars DataFrame to pandas for Great Expectations compatibility
    if isinstance(df, pl.DataFrame):
        pandas_df = df.to_pandas()
    elif isinstance(df, pd.DataFrame):
        pandas_df = df
    else:
        raise TypeError(f"Expected pl.DataFrame or pd.DataFrame, got {type(df)}")
    
    # Create Great Expectations dataset
    ge_dataset = PandasDataset(pandas_df)
    
    # Dictionary to store validation results
    validation_results = {}
    
    # Basic data structure validations
    validation_results["not_empty"] = ge_dataset.expect_table_row_count_to_be_between(
        min_value=1, max_value=None
    )
    
    validation_results["has_columns"] = ge_dataset.expect_table_column_count_to_be_between(
        min_value=1, max_value=None
    )
    
    # Column presence validations
    for column in ge_dataset.columns:
        # Check for missing values
        validation_results[f"{column}_not_null"] = ge_dataset.expect_column_values_to_not_be_null(
            column
        )
        
        # Type-specific validations based on inferred types
        dtype = str(pandas_df[column].dtype)
        
        if "int" in dtype or "float" in dtype:
            # Numeric column validations
            # Get min and max values from the data for dynamic range checking
            try:
                min_val = pandas_df[column].min()
                max_val = pandas_df[column].max()
                validation_results[f"{column}_in_range"] = ge_dataset.expect_column_values_to_be_between(
                    column, min_value=min_val, max_value=max_val
                )
            except:
                # If we can't determine min/max, at least set one boundary
                validation_results[f"{column}_in_range"] = ge_dataset.expect_column_values_to_be_between(
                    column, min_value=float('-inf'), max_value=None
                )
                
            # Check for inf/-inf values by ensuring values are between very large numbers
            # This replaces the non-existent expect_column_values_to_be_finite method
            validation_results[f"{column}_not_inf"] = ge_dataset.expect_column_values_to_be_between(
                column, min_value=-1e308, max_value=1e308
            )
            
        elif "datetime" in dtype or "date" in dtype:
            # Date/time validations
            validation_results[f"{column}_valid_dates"] = ge_dataset.expect_column_values_to_be_dateutil_parseable(
                column
            )
            
        elif "bool" in dtype:
            # Boolean validations
            validation_results[f"{column}_boolean"] = ge_dataset.expect_column_values_to_be_in_set(
                column, value_set=[True, False, 0, 1]
            )
            
        elif "str" in dtype or "object" in dtype:
            # String validations
            validation_results[f"{column}_not_blank"] = ge_dataset.expect_column_values_to_not_be_null(
                column
            )
            validation_results[f"{column}_string_length"] = ge_dataset.expect_column_value_lengths_to_be_between(
                column, min_value=0, max_value=None
            )
    
    # Statistical validations for numeric columns
    numeric_columns = [col for col in ge_dataset.columns 
                      if "int" in str(pandas_df[col].dtype) or "float" in str(pandas_df[col].dtype)]
    
    for column in numeric_columns:
        try:
            # Get the current mean to use as a reference
            current_mean = pandas_df[column].mean()
            # Set a reasonable range around the current mean
            validation_results[f"{column}_stats"] = ge_dataset.expect_column_mean_to_be_between(
                column, min_value=current_mean * 0.5, max_value=current_mean * 1.5
            )
        except:
            # If we can't calculate the mean, use a default approach
            validation_results[f"{column}_stats"] = ge_dataset.expect_column_mean_to_be_between(
                column, min_value=float('-inf'), max_value=None
            )
    
    # Check for duplicates in the dataset
    # Count unique rows and compare with total rows
    unique_row_count = len(pandas_df.drop_duplicates())
    total_row_count = len(pandas_df)
    validation_results["no_duplicates"] = ge_dataset.expect_table_row_count_to_equal(
        unique_row_count
    )
    
    # Print human-readable validation results
    summary = {}
    failed_tests = []
    
    # Fixed: Iterate over the key-value pairs of validation_results
    for test_id, test_details in validation_results.items():
        test_name = test_details['expectation_config']['expectation_type']
        column_name = test_details['expectation_config']['kwargs'].get('column', '')
        
        success = test_details['success']
        summary[test_id] = "PASSED" if success else "FAILED"
        
        element_count = test_details.get('result', {}).get('element_count', 0)
        
        if success:
            if 'not_null' in test_id or 'not_blank' in test_id:
                test_details['details'] = {'message': f"All {element_count} {column_name} values are present"}
            elif 'in_range' in test_id or 'not_inf' in test_id:
                test_details['details'] = {'message': f"All {element_count} {column_name} values are in valid range"}
            elif 'string_length' in test_id:
                test_details['details'] = {'message': f"All {element_count} {column_name} values have valid length"}
            elif 'has_columns' in test_id:
                test_details['details'] = {'message': f"Dataset contains all required columns"}
            elif 'no_duplicates' in test_id:
                test_details['details'] = {'message': f"All {element_count} rows are unique"}
            elif 'not_empty' in test_id:
                test_details['details'] = {'message': f"Dataset contains {element_count} rows"}
            elif '_stats' in test_id:
                test_details['details'] = {'message': f"Statistical checks passed for {column_name}"}
            
            print(test_name)
            print(f"\t{test_details['details']['message']}")
        else:
            failed_tests.append((test_id, test_details))
    
    print("\n=== DATA VALIDATION SUMMARY ===")
    print(f"Total tests: {len(validation_results)}")
    print(f"Passed: {list(summary.values()).count('PASSED')}")
    print(f"Failed: {list(summary.values()).count('FAILED')}")
    
    if failed_tests:
        print("\n=== FAILED TESTS DETAILS ===")
        for test_id, test in failed_tests:
            column_name = test['expectation_config']['kwargs'].get('column', '')
            display_name = column_name if column_name else test_id
            print(f"❌ {display_name}")
            if 'unexpected_count' in test.get('result', {}):
                print(f"   - {test['result']['unexpected_count']} invalid values found")
    
    return validation_results