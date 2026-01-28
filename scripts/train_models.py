"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Model Training Script
"""

import sys
sys.path.append('src')

from data_pipeline.data_generator import TransactionGenerator
from data_pipeline.feature_engineering import FeatureEngineer
from models.ensemble_detector import EnsembleDetector
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import os

def main():
    print("="*60)
    print("ANOMALY DETECTION MODEL TRAINING")
    print("ZeTheta Algorithms Pvt Ltd - CONFIDENTIAL")
    print("="*60)
    
    # Step 1: Generate data
    print("\n[STEP 1] Generating training data...")
    generator = TransactionGenerator(seed=42)
    df = generator.generate_dataset(n_normal=10000, n_fraud=500)
    
    # Step 2: Feature engineering
    print("\n[STEP 2] Engineering features...")
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    # Step 3: Prepare data
    print("\n[STEP 3] Preparing training data...")
    X = engineer.get_feature_matrix(df_features)
    y = df_features['is_fraud'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    print(f"  Fraud rate (train): {y_train.mean()*100:.2f}%")
    print(f"  Fraud rate (test): {y_test.mean()*100:.2f}%")
    
    # Step 4: Train ensemble model
    print("\n[STEP 4] Training ensemble model...")
    model = EnsembleDetector(contamination=0.05)
    model.fit(X_train)
    
    # Step 5: Evaluate
    print("\n[STEP 5] Evaluating model...")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_binary = (y_pred == -1).astype(int)
    
    # Get scores
    y_scores = model.predict_proba(X_test)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_binary)
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    
    print("\nConfusion Matrix:")
    print("                Predicted Normal | Predicted Fraud")
    print(f"Actual Normal:        {cm[0,0]:>6}      |      {cm[0,1]:>6}")
    print(f"Actual Fraud:         {cm[1,0]:>6}      |      {cm[1,1]:>6}")
    
    # Metrics
    tp = cm[1,1]
    fp = cm[0,1]
    tn = cm[0,0]
    fn = cm[1,0]
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    print(f"\nPerformance Metrics:")
    print(f"  Precision:  {precision:.3f} (accuracy of fraud predictions)")
    print(f"  Recall:     {recall:.3f} (% of fraud caught)")
    print(f"  F1-Score:   {f1:.3f} (balanced metric)")
    print(f"  FPR:        {fpr:.3f} (false positive rate)")
    print(f"  Detection Rate: {recall*100:.1f}%")
    
    # Check success criteria
    detection_rate = recall
    false_positive_rate = fpr
    
    print(f"\n{'='*60}")
    print("SUCCESS CRITERIA CHECK")
    print(f"{'='*60}")
    print(f"  Detection Rate: {detection_rate*100:.1f}% (Target: >85%)")
    print(f"  {'✓ PASS' if detection_rate > 0.85 else '✗ FAIL'}")
    print(f"  False Positive Rate: {false_positive_rate*100:.2f}% (Target: <5%)")
    print(f"  {'✓ PASS' if false_positive_rate < 0.05 else '✗ FAIL'}")
    
    # Step 6: Save models
    print(f"\n[STEP 6] Saving models...")
    
    os.makedirs('models', exist_ok=True)
    
    model.if_detector.save('models/isolation_forest.pkl')
    model.lof_detector.save('models/lof.pkl')
    
    # Save feature engineer
    import joblib
    joblib.dump(engineer, 'models/feature_engineer.pkl')
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE!")
    print("="*60)
    print("\nModels saved:")
    print("  - models/isolation_forest.pkl")
    print("  - models/lof.pkl")
    print("  - models/feature_engineer.pkl")

if __name__ == "__main__":
    main()
