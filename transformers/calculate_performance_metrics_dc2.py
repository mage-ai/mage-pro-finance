import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Any


@transformer
def main( Tuple[Any, Any, Any, Any], **kwargs) -> Dict[str, float]:
    """
    Calculate and display classification performance metrics.
    
    Args:
         Tuple containing (X_train, X_test, y_train, y_test, y_pred, y_pred_proba)
    
    Returns:
        Dictionary containing the calculated metrics
    """
    # Unpack the input data
    _, _, _, y_test, y_pred, _ = data
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Create a dictionary to store metrics
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
    
    # Display metrics with explanations and formulas
    print("\n===== Classification Performance Metrics =====\n")
    
    print("Accuracy: {:.4f}".format(accuracy))
    print("Formula: (TP + TN) / (TP + TN + FP + FN)")
    print("Explanation: Proportion of correctly classified instances (both positive and negative) among the total instances.")
    print("When to use: Best when classes are balanced and misclassification costs are similar.\n")
    
    print("Precision: {:.4f}".format(precision))
    print("Formula: TP / (TP + FP)")
    print("Explanation: Proportion of true positive predictions among all positive predictions.")
    print("When to use: When false positives are costly (e.g., spam detection).\n")
    
    print("Recall (Sensitivity): {:.4f}".format(recall))
    print("Formula: TP / (TP + FN)")
    print("Explanation: Proportion of true positives that were correctly identified.")
    print("When to use: When false negatives are costly (e.g., disease detection).\n")
    
    print("F1 Score: {:.4f}".format(f1))
    print("Formula: 2 * (Precision * Recall) / (Precision + Recall)")
    print("Explanation: Harmonic mean of precision and recall, balancing both metrics.")
    print("When to use: When you need a balance between precision and recall.\n")
    
    print("Where:")
    print("TP = True Positives: Correctly predicted positive instances")
    print("TN = True Negatives: Correctly predicted negative instances")
    print("FP = False Positives: Negative instances incorrectly predicted as positive")
    print("FN = False Negatives: Positive instances incorrectly predicted as negative")
    
    return metrics