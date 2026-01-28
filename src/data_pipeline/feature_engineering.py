"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Feature Engineering for Anomaly Detection
"""

import pandas as pd
import numpy as np
from datetime import datetime

class FeatureEngineer:
    """Create features for fraud detection"""
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, df):
        """Create all features from transaction data"""
        
        df = df.copy()
        
        print("Creating features...")
        
        # 1. Temporal Features
        df['hour_of_day'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = df['hour_of_day'].isin(range(0, 6)).astype(int)
        print("  ✓ Temporal features")
        
        # 2. Amount Features
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_sqrt'] = np.sqrt(df['amount'])
        print("  ✓ Amount features")
        
        # 3. User-based Features
        user_stats = df.groupby('user_id').agg({
            'amount': ['mean', 'std', 'count'],
            'transaction_id': 'count'
        }).reset_index()
        user_stats.columns = ['user_id', 'user_avg_amount', 'user_std_amount', 
                              'user_transaction_count', 'user_total_transactions']
        
        df = df.merge(user_stats, on='user_id', how='left')
        
        # Amount deviation from user average
        df['amount_vs_user_avg'] = df['amount'] / (df['user_avg_amount'] + 1)
        df['amount_zscore_user'] = (df['amount'] - df['user_avg_amount']) / (df['user_std_amount'] + 1)
        print("  ✓ User-based features")
        
        # 4. Velocity Features (transactions per user in time windows)
        df = df.sort_values(['user_id', 'timestamp'])
        df['time_since_last_transaction'] = df.groupby('user_id')['timestamp'].diff().dt.total_seconds() / 3600
        df['time_since_last_transaction'] = df['time_since_last_transaction'].fillna(24)
        print("  ✓ Velocity features")
        
        # 5. Categorical Encoding
        df['device_type_encoded'] = pd.Categorical(df['device_type']).codes
        df['merchant_category_encoded'] = pd.Categorical(df['merchant_category']).codes
        df['location_city_encoded'] = pd.Categorical(df['location_city']).codes
        print("  ✓ Categorical features")
        
        # 6. Interaction Features
        df['amount_x_hour'] = df['amount'] * df['hour_of_day']
        df['amount_x_is_night'] = df['amount'] * df['is_night']
        print("  ✓ Interaction features")
        
        # Define feature columns for modeling
        self.feature_names = [
            'amount', 'amount_log', 'amount_sqrt',
            'hour_of_day', 'day_of_week', 'is_weekend', 'is_night',
            'user_avg_amount', 'user_std_amount', 'user_transaction_count',
            'amount_vs_user_avg', 'amount_zscore_user',
            'time_since_last_transaction',
            'device_type_encoded', 'merchant_category_encoded', 'location_city_encoded',
            'amount_x_hour', 'amount_x_is_night'
        ]
        
        print(f"\n✓ Created {len(self.feature_names)} features")
        
        return df
    
    def get_feature_matrix(self, df):
        """Extract feature matrix for modeling"""
        return df[self.feature_names].fillna(0).values
    
    def get_feature_names(self):
        """Get list of feature names"""
        return self.feature_names


if __name__ == "__main__":
    # Test feature engineering
    from data_generator import TransactionGenerator
    
    generator = TransactionGenerator()
    df = generator.generate_dataset(n_normal=1000, n_fraud=50)
    
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    print("\nFeature matrix shape:", engineer.get_feature_matrix(df_features).shape)
    print("Features:", engineer.get_feature_names())
