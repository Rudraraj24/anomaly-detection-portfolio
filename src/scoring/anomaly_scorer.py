"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Anomaly Scoring System
"""

import numpy as np

class AnomalyScorer:
    """Convert raw anomaly scores to risk levels and priorities"""
    
    def __init__(self):
        # Risk level thresholds
        self.thresholds = {
            'CRITICAL': 0.90,
            'HIGH': 0.75,
            'MEDIUM': 0.50,
            'LOW': 0.25
        }
    
    def calculate_composite_score(self, scores_dict):
        """
        Calculate composite score from multiple models
        
        Args:
            scores_dict: Dict with keys like 'isolation_forest', 'lof', etc.
        
        Returns:
            Composite score (0-1)
        """
        # Weighted average
        weights = {
            'isolation_forest': 0.5,
            'lof': 0.3,
            'ensemble': 0.2
        }
        
        composite = sum(
            weights.get(k, 0) * v 
            for k, v in scores_dict.items()
        )
        
        return composite
    
    def assign_risk_level(self, score):
        """
        Assign risk level based on score
        
        Args:
            score: Anomaly score (0-1)
        
        Returns:
            Risk level string
        """
        if score >= self.thresholds['CRITICAL']:
            return 'CRITICAL'
        elif score >= self.thresholds['HIGH']:
            return 'HIGH'
        elif score >= self.thresholds['MEDIUM']:
            return 'MEDIUM'
        elif score >= self.thresholds['LOW']:
            return 'LOW'
        else:
            return 'NORMAL'
    
    def assign_priority(self, risk_level):
        """
        Assign priority for investigation
        
        Args:
            risk_level: Risk level string
        
        Returns:
            Priority (1-5, 1 is highest)
        """
        priority_map = {
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4,
            'NORMAL': 5
        }
        
        return priority_map.get(risk_level, 5)
    
    def score_transactions(self, transactions_df, scores):
        """
        Add scoring columns to transactions dataframe
        
        Args:
            transactions_df: DataFrame with transactions
            scores: Array of anomaly scores
        
        Returns:
            DataFrame with added scoring columns
        """
        df = transactions_df.copy()
        
        df['anomaly_score'] = scores
        df['risk_level'] = df['anomaly_score'].apply(self.assign_risk_level)
        df['priority'] = df['risk_level'].apply(self.assign_priority)
        df['is_anomaly'] = (df['anomaly_score'] >= self.thresholds['MEDIUM']).astype(int)
        
        return df
