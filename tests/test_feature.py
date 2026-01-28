"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Unit Tests for Feature Engineering
"""

import sys
sys.path.append('../src')

from data_pipeline.data_generator import TransactionGenerator
from data_pipeline.feature_engineering import FeatureEngineer
import pandas as pd

def test_feature_engineering():
    """Test feature engineering pipeline"""
    print("\n[TEST] Feature Engineering")
    
    # Generate sample data
    generator = TransactionGenerator(seed=42)
    df = generator.generate_dataset(n_normal=100, n_fraud=5)
    
    # Create features
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    # Get feature matrix
    X = engineer.get_feature_matrix(df_features)
    feature_names = engineer.get_feature_names()
    
    # Assertions
    assert len(df_features) == len(df), "Row count mismatch"
    assert X.shape[0] == len(df), "Feature matrix rows mismatch"
    assert X.shape[1] == len(feature_names), "Feature count mismatch"
    assert 'hour_of_day' in df_features.columns, "Missing temporal feature"
    assert 'amount_log' in df_features.columns, "Missing amount feature"
    assert 'user_avg_amount' in df_features.columns, "Missing user feature"
    
    print(f"  ✓ Created {len(feature_names)} features")
    print(f"  ✓ Feature matrix shape: {X.shape}")
    print("  ✓ All tests passed")
    return True

def test_data_generator():
    """Test data generation"""
    print("\n[TEST] Data Generator")
    
    generator = TransactionGenerator(seed=42)
    df = generator.generate_dataset(n_normal=100, n_fraud=10)
    
    assert len(df) == 110, "Total count mismatch"
    assert (df['is_fraud'] == 0).sum() == 100, "Normal count mismatch"
    assert (df['is_fraud'] == 1).sum() == 10, "Fraud count mismatch"
    assert 'transaction_id' in df.columns, "Missing transaction_id"
    assert 'amount' in df.columns, "Missing amount"
    assert 'timestamp' in df.columns, "Missing timestamp"
    
    print("  ✓ All tests passed")
    return True

def run_all_tests():
    """Run all feature tests"""
    print("="*60)
    print("RUNNING FEATURE TESTS")
    print("="*60)
    
    tests = [
        test_data_generator,
        test_feature_engineering
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
