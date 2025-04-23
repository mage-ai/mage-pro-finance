import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, precision_score, recall_score
from typing import Dict, Tuple, Any, List


@transformer
def main(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Analyze the impact of different classification thresholds on precision and recall.
    
    Args:
         Dictionary containing model predictions and true labels
        
    Returns:
        Dictionary with threshold analysis results and figures
    """
    # Extract data from input
    y_true = data['y_test']
    y_prob = data['y_prob']
    
    # Calculate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    
    # Create a range of thresholds to analyze
    threshold_range = np.linspace(0.1, 0.9, 9)
    threshold_metrics = []
    
    # Calculate precision and recall at different thresholds
    for threshold in threshold_range:
        y_pred = (y_prob >= threshold).astype(int)
        prec = precision_score(y_true, y_pred)
        rec = recall_score(y_true, y_pred)
        threshold_metrics.append({
            'threshold': threshold,
            'precision': prec,
            'recall': rec
        })
    
    # Create visualization of threshold impact
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Precision-Recall curve with thresholds
    ax1.plot(recall, precision, 'b-', linewidth=2)
    ax1.set_xlabel('Recall', fontsize=12)
    ax1.set_ylabel('Precision', fontsize=12)
    ax1.set_title('Precision-Recall Curve', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Add threshold markers
    for metric in threshold_metrics:
        ax1.plot(metric['recall'], metric['precision'], 'ro')
        ax1.annotate(f"t={metric['threshold']:.1f}", 
                    (metric['recall'], metric['precision']),
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center')
    
    # Plot 2: Precision and Recall vs Threshold
    ax2.plot(threshold_range, [m['precision'] for m in threshold_metrics], 'b-', label='Precision')
    ax2.plot(threshold_range, [m['recall'] for m in threshold_metrics], 'r-', label='Recall')
    ax2.set_xlabel('Threshold', fontsize=12)
    ax2.set_ylabel('Score', fontsize=12)
    ax2.set_title('Precision and Recall vs Threshold', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    
    plt.tight_layout()
    
    # Add business scenario examples
    business_scenarios = [
        {
            'name': 'Fraud Detection',
            'priority': 'High Precision',
            'explanation': 'In fraud detection, false positives can lead to legitimate transactions being blocked, '
                          'causing customer frustration. High precision is often prioritized to minimize false alarms, '
                          'even if it means missing some fraud cases (lower recall).',
            'recommended_threshold': 'Higher threshold (e.g., 0.7-0.9)'
        },
        {
            'name': 'Disease Screening',
            'priority': 'High Recall',
            'explanation': 'For medical screening tests, it\'s often better to have false positives (which can be ruled out '
                          'with follow-up tests) than to miss actual cases of disease. High recall is prioritized to ensure '
                          'all potential cases are identified.',
            'recommended_threshold': 'Lower threshold (e.g., 0.2-0.4)'
        },
        {
            'name': 'Content Moderation',
            'priority': 'Balanced Approach',
            'explanation': 'When moderating content on platforms, there\'s a tradeoff between removing harmful content '
                          '(requiring high recall) and not incorrectly removing legitimate content (requiring high precision). '
                          'The optimal threshold depends on platform policies.',
            'recommended_threshold': 'Medium threshold (e.g., 0.4-0.6)'
        }
    ]
    
    # Create a second figure for formulas and explanations
    fig2, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Add mathematical formulas and explanations
    formula_text = """
    Precision-Recall Tradeoff Formulas:
    
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    
    Where:
    TP = True Positives
    FP = False Positives
    FN = False Negatives
    
    As threshold increases:
    - Precision typically increases (fewer false positives)
    - Recall typically decreases (more false negatives)
    """
    
    ax.text(0.1, 0.7, formula_text, fontsize=12, verticalalignment='top')
    
    # Add business scenarios
    scenario_text = "Business Scenario Examples:\n\n"
    for i, scenario in enumerate(business_scenarios):
        scenario_text += f"{i+1}. {scenario['name']} - {scenario['priority']}\n"
        scenario_text += f"   {scenario['explanation']}\n"
        scenario_text += f"   Recommended: {scenario['recommended_threshold']}\n\n"
    
    ax.text(0.1, 0.4, scenario_text, fontsize=12, verticalalignment='top')
    
    plt.tight_layout()
    
    # Return results
    return {
        'threshold_metrics': threshold_metrics,
        'precision_recall_curve': (precision, recall, thresholds),
        'business_scenarios': business_scenarios,
        'figures': [fig, fig2]
    }