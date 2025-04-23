import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix
from typing import Dict, Tuple, Any


@data_exporter
def main(y_true_y_pred_proba: Tuple[np.ndarray, np.ndarray, np.ndarray], **kwargs) -> Dict[str, Any]:
    """
    Generate and visualize a confusion matrix with clear labels for TP, FP, TN, FN.
    
    Args:
        y_true_y_pred_proba: Tuple containing (y_true, y_pred, y_pred_proba)
    
    Returns:
        Dictionary containing the confusion matrix and figure
    """
    # Extract data from input tuple
    y_true, y_pred, y_pred_proba = y_true_y_pred_proba
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Create figure and axis
    plt.figure(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    
    # Add labels and title
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    
    # Set tick labels
    plt.xticks([0.5, 1.5], ['Negative (0)', 'Positive (1)'])
    plt.yticks([0.5, 1.5], ['Negative (0)', 'Positive (1)'])
    
    # Add annotations for TP, FP, TN, FN
    plt.text(1.5, 0.5, 'False Positive (FP)', 
             horizontalalignment='center', verticalalignment='center', 
             bbox=dict(facecolor='white', alpha=0.5))
    
    plt.text(0.5, 0.5, 'True Negative (TN)', 
             horizontalalignment='center', verticalalignment='center', 
             bbox=dict(facecolor='white', alpha=0.5))
    
    plt.text(1.5, 1.5, 'True Positive (TP)', 
             horizontalalignment='center', verticalalignment='center', 
             bbox=dict(facecolor='white', alpha=0.5))
    
    plt.text(0.5, 1.5, 'False Negative (FN)', 
             horizontalalignment='center', verticalalignment='center', 
             bbox=dict(facecolor='white', alpha=0.5))
    
    # Add explanation text
    plt.figtext(0.5, 0.01, 
                'TP: Correctly predicted positive\nFP: Incorrectly predicted positive\n'
                'TN: Correctly predicted negative\nFN: Incorrectly predicted negative',
                ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    # Save figure
    plt.tight_layout()
    
    # Return results
    return {
        'confusion_matrix': cm,
        'figure': plt.gcf()
    }