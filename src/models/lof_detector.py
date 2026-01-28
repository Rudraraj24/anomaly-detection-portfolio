"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Local Outlier Factor (LOF) Detector

LOF detects anomalies by comparing local density of a point to its neighbors.
Points in low-density regions relative to neighbors are anomalies.
"""

from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib

class LOFDetector:
    """Local Outlier Factor anomaly detector"""
    
    def __init__(self, n_neighbors=20, contamination=0.05):
        """
        Args:
            n_neighbors: Number of neighbors to consider for density
            contamination: Expected proportion of anomalies
        """
        self.n_neighbors = n_neighbors
        self.contamination = contamination
        
        self.model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=contamination,
            novelty=True,  # Enable predict on new data
            n_jobs=-1
        )
        
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, X):
        """Train LOF detector"""
        print(f"Training LOF...")
        print(f"  Data shape: {X.shape}")
        print(f"  N neighbors: {self.n_neighbors}")
        print(f"  Contamination: {self.contamination}")
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        
        self.is_fitted = True
        print("✓ LOF trained")
    
    def predict(self, X):
        """Predict anomalies"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return predictions
    
    def predict_proba(self, X):
        """Get anomaly scores"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X_scaled = self.scaler.transform(X)
        scores = -self.model.decision_function(X_scaled)
        
        # Normalize to [0, 1]
        scores_normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return scores_normalized
    
    def save(self, filepath):
        """Save model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'n_neighbors': self.n_neighbors,
            'contamination': self.contamination
        }, filepath)
        print(f"✓ Saved to {filepath}")
    
    def load(self, filepath):
        """Load model"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.n_neighbors = data['n_neighbors']
        self.contamination = data['contamination']
        self.is_fitted = True
        print(f"✓ Loaded from {filepath}")
