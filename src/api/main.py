"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
FastAPI Application for Anomaly Detection
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sys
sys.path.append('..')

from models.isolation_forest_detector import IsolationForestDetector
from scoring.anomaly_scorer import AnomalyScorer
from alerts.alert_manager import AlertManager
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Initialize FastAPI
app = FastAPI(
    title="Anomaly Detection API",
    description="Real-time fraud detection system - ZeTheta Algorithms",
    version="1.0.0"
)

# Load models on startup
try:
    if_detector = IsolationForestDetector()
    if_detector.load('../../models/isolation_forest.pkl')
    feature_engineer = joblib.load('../../models/feature_engineer.pkl')
    scorer = AnomalyScorer()
    alert_manager = AlertManager()
    print("✓ Models loaded successfully")
except Exception as e:
    print(f"Warning: Could not load models: {e}")
    if_detector = None
    feature_engineer = None

# Pydantic models for request/response
class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant_category: str
    location_city: str
    device_type: str
    timestamp: str = None

class AnomalyResponse(BaseModel):
    transaction_id: str
    anomaly_score: float
    risk_level: str
    priority: int
    is_anomaly: bool
    alert_created: bool

class BatchRequest(BaseModel):
    transactions: List[Transaction]

# Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Anomaly Detection API",
        "version": "1.0.0",
        "company": "ZeTheta Algorithms Pvt Ltd"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models_loaded": if_detector is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/detect", response_model=AnomalyResponse)
def detect_anomaly(transaction: Transaction):
    """
    Detect anomaly in a single transaction
    
    Returns anomaly score, risk level, and creates alert if needed
    """
    if if_detector is None or feature_engineer is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Convert to DataFrame
        trans_dict = transaction.dict()
        trans_dict['timestamp'] = trans_dict.get('timestamp') or datetime.now().isoformat()
        trans_dict['is_fraud'] = 0  # Unknown at detection time
        
        df = pd.DataFrame([trans_dict])
        
        # Engineer features
        df_features = feature_engineer.create_features(df)
        X = feature_engineer.get_feature_matrix(df_features)
        
        # Predict
        prediction = if_detector.predict(X)[0]
        score = float(if_detector.predict_proba(X)[0])
        
        # Score
        risk_level = scorer.assign_risk_level(score)
        priority = scorer.assign_priority(risk_level)
        is_anomaly = score >= scorer.thresholds['MEDIUM']
        
        # Create alert if high risk
        alert_created = False
        if risk_level in ['CRITICAL', 'HIGH']:
            alert_id = alert_manager.create_alert(
                transaction_id=transaction.transaction_id,
                score=score,
                risk_level=risk_level,
                priority=priority
            )
            alert_created = alert_id is not None
        
        return AnomalyResponse(
            transaction_id=transaction.transaction_id,
            anomaly_score=score,
            risk_level=risk_level,
            priority=priority,
            is_anomaly=is_anomaly,
            alert_created=alert_created
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

@app.post("/detect/batch")
def detect_batch(request: BatchRequest):
    """
    Detect anomalies in batch of transactions
    
    More efficient for processing multiple transactions at once
    """
    if if_detector is None or feature_engineer is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Convert to DataFrame
        trans_list = [t.dict() for t in request.transactions]
        for t in trans_list:
            t['timestamp'] = t.get('timestamp') or datetime.now().isoformat()
            t['is_fraud'] = 0
        
        df = pd.DataFrame(trans_list)
        
        # Engineer features
        df_features = feature_engineer.create_features(df)
        X = feature_engineer.get_feature_matrix(df_features)
        
        # Predict
        predictions = if_detector.predict(X)
        scores = if_detector.predict_proba(X)
        
        # Score all transactions
        df_scored = scorer.score_transactions(df_features, scores)
        
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
        
        # Prepare response
        results = []
        for idx, row in df_scored.iterrows():
            results.append({
                'transaction_id': row['transaction_id'],
                'anomaly_score': float(row['anomaly_score']),
                'risk_level': row['risk_level'],
                'priority': int(row['priority']),
                'is_anomaly': bool(row['is_anomaly'])
            })
        
        return {
            'total_transactions': len(df),
            'anomalies_detected': int((predictions == -1).sum()),
            'alerts_created': alerts_created,
            'results': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch detection error: {str(e)}")

@app.get("/alerts")
def get_alerts(limit: int = 100):
    """Get open alerts"""
    try:
        alerts_df = alert_manager.get_open_alerts(limit=limit)
        return {
            'count': len(alerts_df),
            'alerts': alerts_df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@app.get("/alerts/statistics")
def get_alert_statistics():
    """Get alert statistics"""
    try:
        stats_df = alert_manager.get_alert_statistics()
        return {
            'statistics': stats_df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@app.put("/alerts/{alert_id}")
def update_alert(alert_id: int, status: str, resolution: str = None, notes: str = None):
    """Update alert status"""
    try:
        alert_manager.update_alert_status(
            alert_id=alert_id,
            status=status,
            resolution=resolution,
            notes=notes
        )
        return {
            'alert_id': alert_id,
            'status': status,
            'message': 'Alert updated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")

@app.get("/models/info")
def model_info():
    """Get model information"""
    if if_detector is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        'isolation_forest': {
            'contamination': if_detector.contamination,
            'n_estimators': if_detector.n_estimators,
            'is_fitted': if_detector.is_fitted
        },
        'features': feature_engineer.get_feature_names() if feature_engineer else []
    }

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
