"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
Database initialization script
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database schema"""
    
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'anomaly_detection'),
        'user': os.getenv('DB_USER', 'anomaly_user'),
        'password': os.getenv('DB_PASSWORD', 'Rudra@2404')
    }
    
    try:
        print("="*60)
        print("ZeTheta Algorithms - Database Setup")
        print("STRICTLY CONFIDENTIAL")
        print("="*60)
        
        print("\nConnecting to database...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connected successfully")
        
        print("\nReading schema file...")
        with open('src/data_pipeline/schema.sql', 'r') as f:
            schema_sql = f.read()
        print("✓ Schema file loaded")
        
        print("\nCreating database schema...")
        cursor.execute(schema_sql)
        print("✓ Schema executed")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n{'='*60}")
        print(f"✓ DATABASE SETUP COMPLETE!")
        print(f"{'='*60}")
        print(f"\nCreated {len(tables)} tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        print(f"\n{'='*60}")
        print("Database is ready for use!")
        print(f"{'='*60}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ ERROR")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check PostgreSQL is running")
        print("2. Verify credentials in .env file")
        print("3. Ensure database 'anomaly_detection' exists")
        print("4. Check user 'anomaly_user' has permissions")
        raise

if __name__ == "__main__":
    init_database()
