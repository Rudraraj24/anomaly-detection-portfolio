"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Unit Tests for Models
"""

import sys
sys.path.append('../src')

from models.isolation_forest_detector import IsolationForestDetector
from models.lof_detector import LOFDetector
from models.ensemble_detector import EnsembleDetector
from sklearn.datasets import make_classification
import numpy as np

def test_isolation_forest():
    """Test Isolation Forest detector"""
    print("\n[TEST] Isolation Forest Detector")
    
    # Generate test data
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        weights=[0.95, 0.05],
        random_state=42
    )
    
    # Train
    detector = IsolationForestDetector(contamination=0.05)
    detector.fit(X)
    
    # Predict
    predictions = detector.predict(X)
    scores = detector.predict_proba(X)
    
    # Assertions
    assert detector.is_fitted == True, "Model should be fitted"
    assert len(predictions) == len(X), "Predictions length mismatch"
    assert len(scores) == len(X), "Scores length mismatch"
    assert ((predictions == 1) | (predictions == -1)).all(), "Invalid predictions"
    assert (scores >= 0).all() and (scores <= 1).all(), "Scores out of range"
    
    print("  ✓ All tests passed")
    return True

def test_lof_detector():
    """Test LOF detector"""
    print("\n[TEST] LOF Detector")
    
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        weights=[0.95, 0.05],
        random_state=42
    )
    
    detector = LOFDetector(n_neighbors=20, contamination=0.05)
    detector.fit(X)
    
    predictions = detector.predict(X)
    scores = detector.predict_proba(X)
    
    assert detector.is_fitted == True
    assert len(predictions) == len(X)
    assert (scores >= 0).all() and (scores <= 1).all()
    
    print("  ✓ All tests passed")
    return True

def test_ensemble_detector():
    """Test Ensemble detector"""
    print("\n[TEST] Ensemble Detector")
    
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        weights=[0.95, 0.05],
        random_state=42
    )
    
    detector = EnsembleDetector(contamination=0.05)
    detector.fit(X)
    
    predictions = detector.predict(X)
    scores = detector.predict_proba(X)
    individual_scores = detector.get_individual_scores(X)
    
    assert detector.is_fitted == True
    assert len(predictions) == len(X)
    assert 'isolation_forest' in individual_scores
    assert 'lof' in individual_scores
    assert 'ensemble' in individual_scores
    
    print("  ✓ All tests passed")
    return True

def run_all_tests():
    """Run all model tests"""
    print("="*60)
    print("RUNNING MODEL TESTS")
    print("="*60)
    
    tests = [
        test_isolation_forest,
        test_lof_detector,
        test_ensemble_detector
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
