"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Ensemble Anomaly Detector - Combines multiple algorithms
"""

import numpy as np
from .isolation_forest_detector import IsolationForestDetector
from .lof_detector import LOFDetector

class EnsembleDetector:
    """Combine multiple detectors for robust anomaly detection"""
    
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        
        # Initialize detectors
        self.if_detector = IsolationForestDetector(contamination=contamination)
        self.lof_detector = LOFDetector(contamination=contamination)
        
        # Weights for each detector (can be tuned)
        self.weights = {
            'isolation_forest': 0.6,
            'lof': 0.4
        }
        
        self.is_fitted = False
    
    def fit(self, X):
        """Train all detectors"""
        print("="*60)
        print("Training Ensemble Detector")
        print("="*60)
        
        # Train Isolation Forest
        print("\n[1/2] Isolation Forest")
        self.if_detector.fit(X)
        
        # Train LOF
        print("\n[2/2] Local Outlier Factor")
        self.lof_detector.fit(X)
        
        self.is_fitted = True
        print("\n" + "="*60)
        print("✓ Ensemble training complete")
        print("="*60)
    
    def predict(self, X):
        """Predict using ensemble voting"""
        if not self.is_fitted:
            raise ValueError("Models must be fitted first")
        
        # Get predictions from each model
        if_pred = self.if_detector.predict(X)
        lof_pred = self.lof_detector.predict(X)
        
        # Majority voting
        ensemble_pred = np.where(
            (if_pred + lof_pred) < 0,  # Both predict -1 (anomaly)
            -1,
            1
        )
        
        return ensemble_pred
    
    def predict_proba(self, X):
        """Get ensemble anomaly scores"""
        if not self.is_fitted:
            raise ValueError("Models must be fitted first")
        
        # Get scores from each model
        if_scores = self.if_detector.predict_proba(X)
        lof_scores = self.lof_detector.predict_proba(X)
        
        # Weighted average
        ensemble_scores = (
            self.weights['isolation_forest'] * if_scores +
            self.weights['lof'] * lof_scores
        )
        
        return ensemble_scores
    
    def get_individual_scores(self, X):
        """Get scores from each detector separately"""
        if not self.is_fitted:
            raise ValueError("Models must be fitted first")
        
        return {
            'isolation_forest': self.if_detector.predict_proba(X),
            'lof': self.lof_detector.predict_proba(X),
            'ensemble': self.predict_proba(X)
        }
