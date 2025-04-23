import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from typing import Dict, Tuple, Any


@transformer
def main(data=None, **kwargs) -> Dict[str, Any]:
    """
    Split the dataset into training and testing sets, train a logistic regression model,
    and generate predictions.
    
    Args:
         Input data (not used in this case as we're loading data directly)
        **kwargs: Additional keyword arguments
        
    Returns:
        Dict containing X_train, X_test, y_train, y_test, y_pred, and model
    """
    # Load the Titanic dataset
    data = pd.read_csv('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
    
    # Basic preprocessing
    data = data.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1)
    data = pd.get_dummies(data, columns=['Sex', 'Embarked'], drop_first=True)
    data = data.fillna(data.mean())
    
    # Define features and target
    X = data.drop('Survived', axis=1)
    y = data['Survived']
    
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Train a logistic regression model
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    # Generate predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Return the results
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba,
        'model': model
    }