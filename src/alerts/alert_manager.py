"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Alert Management System
"""

import pandas as pd
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class AlertManager:
    """Manage fraud alerts and investigations"""
    
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'anomaly_detection'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
    
    def create_alert(self, transaction_id, score, risk_level, priority):
        """
        Create a new alert in database
        
        Args:
            transaction_id: Transaction ID
            score: Anomaly score
            risk_level: Risk level string
            priority: Priority (1-5)
        
        Returns:
            alert_id
        """
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            
            # Determine alert type based on score
            alert_type = 'MODEL_BASED'
            
            # Determine severity
            severity_map = {
                'CRITICAL': 'CRITICAL',
                'HIGH': 'HIGH',
                'MEDIUM': 'MEDIUM',
                'LOW': 'LOW'
            }
            severity = severity_map.get(risk_level, 'LOW')
            
            # Insert alert
            cursor.execute("""
                INSERT INTO alerts (
                    transaction_id, alert_type, severity, priority, status
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING alert_id
            """, (transaction_id, alert_type, severity, priority, 'OPEN'))
            
            alert_id = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return alert_id
            
        except Exception as e:
            print(f"Error creating alert: {e}")
            return None
    
    def get_open_alerts(self, limit=100):
        """Get open alerts ordered by priority"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            
            query = """
                SELECT 
                    alert_id,
                    transaction_id,
                    severity,
                    priority,
                    created_at
                FROM alerts
                WHERE status = 'OPEN'
                ORDER BY priority ASC, created_at DESC
                LIMIT %s
            """
            
            df = pd.read_sql(query, conn, params=(limit,))
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return pd.DataFrame()
    
    def update_alert_status(self, alert_id, status, resolution=None, notes=None):
        """Update alert status"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE alerts
                SET status = %s,
                    resolution = %s,
                    investigation_notes = %s,
                    resolved_at = CASE WHEN %s IN ('RESOLVED', 'FALSE_POSITIVE') 
                                      THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE alert_id = %s
            """, (status, resolution, notes, status, alert_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Alert {alert_id} updated to {status}")
            
        except Exception as e:
            print(f"Error updating alert: {e}")
    
    def get_alert_statistics(self):
        """Get alert statistics"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            
            query = """
                SELECT 
                    status,
                    severity,
                    COUNT(*) as count
                FROM alerts
                GROUP BY status, severity
                ORDER BY status, severity
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return pd.DataFrame()
