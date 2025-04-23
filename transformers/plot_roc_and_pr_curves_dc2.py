import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, precision_recall_curve, auc, roc_auc_score, average_precision_score
from typing import Dict, Tuple, Any


@transformer
def main(results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Generate ROC and Precision-Recall curves for a classification model.
    
    Args:
        results: Dictionary containing model prediction results with y_test and y_pred_proba
        
    Returns:
        Dictionary with AUC scores and figure objects
    """
    # Extract test labels and prediction probabilities
    y_test = results['y_test']
    y_pred_proba = results['y_pred_proba']
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Generate ROC curve
    fpr, tpr, thresholds_roc = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    # Plot ROC curve
    ax1.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
    ax1.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('False Positive Rate')
    ax1.set_ylabel('True Positive Rate')
    ax1.set_title('Receiver Operating Characteristic (ROC) Curve')
    ax1.legend(loc="lower right")
    
    # Generate Precision-Recall curve
    precision, recall, thresholds_pr = precision_recall_curve(y_test, y_pred_proba)
    avg_precision = average_precision_score(y_test, y_pred_proba)
    
    # Plot Precision-Recall curve
    ax2.plot(recall, precision, color='green', lw=2, label=f'PR curve (AP = {avg_precision:.3f})')
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel('Recall')
    ax2.set_ylabel('Precision')
    ax2.set_title('Precision-Recall Curve')
    ax2.legend(loc="lower left")
    
    plt.tight_layout()
    
    # Add explanatory text to the figure
    plt.figtext(0.5, 0.01, """
    ROC Curve: Shows the tradeoff between True Positive Rate (sensitivity) and False Positive Rate (1-specificity).
    - AUC (Area Under Curve): Measures the model's ability to discriminate between classes.
    - AUC of 1.0 represents a perfect model, while 0.5 represents a random classifier.
    
    Precision-Recall Curve: Shows the tradeoff between precision (positive predictive value) and recall (sensitivity).
    - Particularly useful for imbalanced datasets where negative class is more common.
    - Different thresholds prioritize either precision or recall based on business needs.
    """, ha='center', fontsize=10, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
    
    plt.subplots_adjust(bottom=0.3)
    
    # Create a dictionary with results
    curve_results = {
        'roc_auc': roc_auc,
        'average_precision': avg_precision,
        'roc_curve_data': {
            'fpr': fpr,
            'tpr': tpr,
            'thresholds': thresholds_roc
        },
        'pr_curve_data': {
            'precision': precision,
            'recall': recall,
            'thresholds': thresholds_pr
        },
        'figure': fig
    }
    
    # Display the figure
    plt.show()
    
    return curve_results