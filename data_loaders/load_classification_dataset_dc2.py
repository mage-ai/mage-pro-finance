import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from typing import Dict, Any, Tuple


@data_loader
def main(**kwargs) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Load the Breast Cancer Wisconsin dataset for classification tasks.
    
    Returns:
        Tuple containing:
        - DataFrame with feature data
        - Array with target labels (0 for malignant, 1 for benign)
    """
    # Load the breast cancer dataset
    cancer = load_breast_cancer()
    
    # Create a DataFrame with the feature data
    feature_names = cancer.feature_names
    data = pd.DataFrame(cancer.data, columns=feature_names)
    
    # Get the target labels
    target = cancer.target
    
    # Add information about the dataset
    print(f"Dataset loaded: {cancer.DESCR.split('Description')[0].strip()}")
    print(f"Number of samples: {len(data)}")
    print(f"Number of features: {len(feature_names)}")
    print(f"Target distribution: {np.bincount(target)}")
    print(f"Class names: {cancer.target_names}")
    
    return data, target