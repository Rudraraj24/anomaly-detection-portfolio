"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Isolation Forest Anomaly Detector
"""

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib

class IsolationForestDetector:
    """
    Isolation Forest for anomaly detection
    
    Algorithm works by:
    1. Randomly selecting features
    2. Randomly selecting split values
    3. Isolating points - anomalies are easier to isolate (fewer splits needed)
    4. Anomaly score based on average path length across trees
    """
    
    def __init__(self, contamination=0.05, n_estimators=100, random_state=42):
        """
        Args:
            contamination: Expected proportion of anomalies (0.01-0.5)
            n_estimators: Number of isolation trees
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1  # Use all CPU cores
        )
        
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, X):
        """
        Train the isolation forest
        
        Args:
            X: Feature matrix (n_samples, n_features)
        """
        print(f"Training Isolation Forest...")
        print(f"  Data shape: {X.shape}")
        print(f"  Contamination: {self.contamination}")
        print(f"  N estimators: {self.n_estimators}")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        
        self.is_fitted = True
        print("✓ Model trained")
    
    def predict(self, X):
        """
        Predict anomalies
        
        Args:
            X: Feature matrix
            
        Returns:
            predictions: 1 for normal, -1 for anomaly
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Get anomaly scores (lower = more anomalous)
        
        Args:
            X: Feature matrix
            
        Returns:
            scores: Anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        scores = self.model.decision_function(X_scaled)
        
        # Convert to probabilities (0-1 range, higher = more anomalous)
        # Normalize scores to [0, 1]
        scores_normalized = (scores - scores.min()) / (scores.max() - scores.min())
        anomaly_proba = 1 - scores_normalized  # Invert so high = anomalous
        
        return anomaly_proba
    
    def save(self, filepath):
        """Save model to disk"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators
        }
        
        joblib.dump(model_data, filepath)
        print(f"✓ Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model from disk"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.contamination = model_data['contamination']
        self.n_estimators = model_data['n_estimators']
        self.is_fitted = True
        
        print(f"✓ Model loaded from {filepath}")


if __name__ == "__main__":
    # Test the detector
    from sklearn.datasets import make_classification
    
    # Generate test data
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_clusters_per_class=1,
        weights=[0.95, 0.05],
        random_state=42
    )
    
    # Train
    detector = IsolationForestDetector(contamination=0.05)
    detector.fit(X)
    
    # Predict
    predictions = detector.predict(X)
    scores = detector.predict_proba(X)
    
    print(f"\nDetected {(predictions == -1).sum()} anomalies out of {len(X)} transactions")
    print(f"Anomaly scores range: {scores.min():.3f} to {scores.max():.3f}")
