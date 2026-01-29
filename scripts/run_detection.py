"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Run Anomaly Detection on New Data
"""

import sys
sys.path.append('src')

from data_pipeline.data_generator import TransactionGenerator
from models.isolation_forest_detector import IsolationForestDetector
from scoring.anomaly_scorer import AnomalyScorer
from alerts.alert_manager import AlertManager
import joblib
import pandas as pd
import numpy as np

def main():
    print("="*60)
    print("ANOMALY DETECTION SYSTEM")
    print("ZeTheta Algorithms Pvt Ltd - CONFIDENTIAL")
    print("="*60)
    
    # Step 1: Load models
    print("\n[STEP 1] Loading trained models...")
    
    try:
        if_detector = IsolationForestDetector()
        if_detector.load('models/isolation_forest.pkl')
        
        feature_engineer = joblib.load('models/feature_engineer.pkl')
        
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        print("Please run 'python scripts/train_models_aggressive.py' first")
        return
    
    # Step 2: Generate new transactions to score
    print("\n[STEP 2] Generating new transactions...")
    generator = TransactionGenerator(seed=999)
    df = generator.generate_dataset(n_normal=100, n_fraud=5)
    print(f"  Generated {len(df)} transactions to analyze")
    
    # Step 3: Engineer features
    print("\n[STEP 3] Engineering features...")
    df_features = feature_engineer.create_features(df)
    X = feature_engineer.get_feature_matrix(df_features)
    
    # Step 4: Detect anomalies with optimal threshold
    print("\n[STEP 4] Running anomaly detection...")
    
    # Load optimal threshold
    try:
        threshold_data = joblib.load('models/optimal_threshold.pkl')
        optimal_threshold = threshold_data['threshold']
        print(f"  Using optimal threshold: {optimal_threshold:.4f}")
    except:
        optimal_threshold = 0.5
        print(f"  Using default threshold: {optimal_threshold}")
    
    # Get scores
    scores = if_detector.predict_proba(X)
    
    # Apply optimal threshold
    predictions = np.where(scores >= optimal_threshold, -1, 1)
    
    # Step 5: Score and prioritize
    print("\n[STEP 5] Scoring and prioritizing...")
    scorer = AnomalyScorer()
    df_scored = scorer.score_transactions(df_features, scores)
    
    # Step 6: Generate alerts
    print("\n[STEP 6] Generating alerts...")
    alert_manager = AlertManager()
    
    # Create alerts for high-risk transactions
    alerts_created = 0
    for idx, row in df_scored.iterrows():
        if row['risk_level'] in ['CRITICAL', 'HIGH']:
            alert_id = alert_manager.create_alert(
                transaction_id=row['transaction_id'],
                score=row['anomaly_score'],
                risk_level=row['risk_level'],
                priority=row['priority']
            )
            if alert_id:
                alerts_created += 1
    
    # Step 7: Results summary
    print("\n" + "="*60)
    print("DETECTION RESULTS")
    print("="*60)
    
    print(f"\nTransactions Analyzed: {len(df)}")
    print(f"Anomalies Detected: {(predictions == -1).sum()}")
    print(f"Alerts Created: {alerts_created}")
    
    print("\nRisk Distribution:")
    risk_dist = df_scored['risk_level'].value_counts()
    for level, count in risk_dist.items():
        print(f"  {level}: {count}")
    
    print("\nTop 10 Highest Risk Transactions:")
    top_risks = df_scored.nlargest(10, 'anomaly_score')[
        ['transaction_id', 'amount', 'anomaly_score', 'risk_level', 'is_fraud']
    ]
    print(top_risks.to_string(index=False))
    
    # Actual performance
    actual_fraud = df_scored['is_fraud'].sum()
    detected_fraud = df_scored[df_scored['is_anomaly'] == 1]['is_fraud'].sum()
    
    print(f"\nActual Fraud in Batch: {actual_fraud}")
    print(f"Fraud Caught: {detected_fraud}")
    if actual_fraud > 0:
        detection_rate = detected_fraud / actual_fraud * 100
        print(f"Detection Rate: {detection_rate:.1f}%")
        
        if detection_rate >= 80:
            print("✓ EXCELLENT - Catching most fraud!")
        elif detection_rate >= 60:
            print("✓ GOOD - Decent detection rate")
        else:
            print("⚠ WARNING - Low detection rate, consider retraining")
    
    print("\n" + "="*60)
    print("✓ DETECTION COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
