"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Synthetic Transaction Data Generator for Training
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TransactionGenerator:
    """Generate realistic synthetic transaction data"""
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        self.seed = seed
    
    def generate_normal_transactions(self, n=10000):
        """Generate normal transaction patterns"""
        
        # Base time
        start_date = datetime.now() - timedelta(days=30)
        
        transactions = []
        for i in range(n):
            transaction = {
                'transaction_id': f'TXN_{i:06d}',
                'user_id': f'USER_{np.random.randint(1, 1000):04d}',
                'timestamp': start_date + timedelta(
                    days=np.random.randint(0, 30),
                    hours=np.random.randint(6, 22),  # Normal hours
                    minutes=np.random.randint(0, 60)
                ),
                'amount': np.random.lognormal(mean=3.5, sigma=1.2),
                'merchant_category': np.random.choice([
                    'grocery', 'restaurant', 'gas', 'retail', 'entertainment'
                ]),
                'location_city': np.random.choice([
                    'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'
                ]),
                'device_type': np.random.choice(['mobile', 'web', 'pos'], p=[0.6, 0.3, 0.1]),
                'is_fraud': 0
            }
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def generate_fraudulent_transactions(self, n=500):
        """Generate fraudulent transaction patterns"""
        
        start_date = datetime.now() - timedelta(days=30)
        
        transactions = []
        for i in range(n):
            transaction = {
                'transaction_id': f'TXN_FRAUD_{i:06d}',
                'user_id': f'USER_{np.random.randint(1, 1000):04d}',
                'timestamp': start_date + timedelta(
                    days=np.random.randint(0, 30),
                    hours=np.random.randint(0, 6),  # Unusual hours (late night)
                    minutes=np.random.randint(0, 60)
                ),
                'amount': np.random.lognormal(mean=5.5, sigma=1.5),  # Larger amounts
                'merchant_category': np.random.choice([
                    'electronics', 'jewelry', 'online', 'international'
                ]),
                'location_city': np.random.choice([
                    'Unknown', 'International', 'Delhi', 'Mumbai'
                ]),
                'device_type': np.random.choice(['web', 'mobile'], p=[0.8, 0.2]),
                'is_fraud': 1
            }
            transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def generate_dataset(self, n_normal=10000, n_fraud=500):
        """Generate complete dataset with normal and fraud transactions"""
        
        print(f"Generating {n_normal} normal transactions...")
        normal_df = self.generate_normal_transactions(n_normal)
        
        print(f"Generating {n_fraud} fraudulent transactions...")
        fraud_df = self.generate_fraudulent_transactions(n_fraud)
        
        # Combine and shuffle
        df = pd.concat([normal_df, fraud_df], ignore_index=True)
        df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
        
        print(f"\nDataset created:")
        print(f"  Total transactions: {len(df)}")
        print(f"  Normal: {(df['is_fraud']==0).sum()} ({(df['is_fraud']==0).sum()/len(df)*100:.1f}%)")
        print(f"  Fraud: {(df['is_fraud']==1).sum()} ({(df['is_fraud']==1).sum()/len(df)*100:.1f}%)")
        
        return df
    
    def save_to_database(self, df, conn):
        """Save generated data to PostgreSQL"""
        
        from sqlalchemy import create_engine
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Create engine
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        
        # Save to database
        df.to_sql('transactions', engine, if_exists='append', index=False)
        print(f"✓ Saved {len(df)} transactions to database")


if __name__ == "__main__":
    # Test the generator
    generator = TransactionGenerator()
    df = generator.generate_dataset(n_normal=1000, n_fraud=50)
    
    # Save sample
    df.to_csv('data/processed/sample_transactions.csv', index=False)
    print("\n✓ Sample saved to data/processed/sample_transactions.csv")
