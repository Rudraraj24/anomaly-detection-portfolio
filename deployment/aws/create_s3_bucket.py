"""
STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
S3 bucket creation script
"""

import boto3
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

load_dotenv()

def create_s3_bucket():
    """Create S3 bucket for anomaly detection data"""
    
    # Bucket name (must be globally unique and lowercase)
    bucket_name = f"zetheta-anomaly-detection-{datetime.now().strftime('%Y%m%d%H%M%S')}".lower()
    region = os.getenv('AWS_REGION', 'ap-south-1')
    
    # Get credentials
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not access_key or not secret_key:
        print("✗ Error: AWS credentials not found in .env file")
        print("Please add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to your .env file")
        sys.exit(1)
    
    # Initialize S3 client
    try:
        s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        print(f"✓ AWS credentials validated")
    except Exception as e:
        print(f"✗ Error connecting to AWS: {e}")
        print("Please check your AWS credentials in .env file")
        sys.exit(1)
    
    try:
        # Create bucket
        print(f"\nCreating S3 bucket: {bucket_name}")
        print(f"Region: {region}")
        
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✓ Bucket created: {bucket_name}")
        
        # Enable versioning
        print("\n[1/5] Enabling versioning...")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✓ Versioning enabled")
        
        # Enable encryption
        print("\n[2/5] Enabling encryption...")
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    },
                    'BucketKeyEnabled': True
                }]
            }
        )
        print("✓ Encryption enabled (AES256)")
        
        # Block public access
        print("\n[3/5] Blocking public access...")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✓ Public access blocked")
        
        # Add bucket policy
        print("\n[4/5] Adding encryption enforcement policy...")
        import json
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "DenyUnencryptedObjectUploads",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "StringNotEquals": {
                        "s3:x-amz-server-side-encryption": "AES256"
                    }
                }
            }]
        }
        
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✓ Encryption policy enforced")
        
        # Create folders
        print("\n[5/5] Creating folder structure...")
        folders = [
            'raw-data/',
            'processed-data/',
            'features/',
            'models/',
            'logs/',
            'alerts/',
            'reports/',
            'backups/'
        ]
        
        for folder in folders:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=folder,
                ServerSideEncryption='AES256'
            )
        
        print(f"✓ Created {len(folders)} folders")
        
        # Summary
        print("\n" + "="*60)
        print("✓ S3 BUCKET CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nBucket Name: {bucket_name}")
        print(f"Region: {region}")
        print(f"\nSecurity Features:")
        print(f"  ✓ Versioning: Enabled")
        print(f"  ✓ Encryption: AES256")
        print(f"  ✓ Public access: Blocked")
        print(f"  ✓ Folders: {len(folders)} created")
        
        print(f"\n" + "="*60)
        print("Update your .env file with:")
        print("="*60)
        print(f"S3_BUCKET={bucket_name}")
        print("="*60)
        
        # Update .env
        update = input("\nUpdate .env file automatically? (yes/no): ").lower()
        if update in ['yes', 'y']:
            update_env_file(bucket_name)
        
        return bucket_name
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

def update_env_file(bucket_name):
    """Update .env file with bucket name"""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('S3_BUCKET='):
                lines[i] = f'S3_BUCKET={bucket_name}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nS3_BUCKET={bucket_name}\n')
        
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print(f"✓ .env file updated!")
        
    except Exception as e:
        print(f"✗ Could not update .env: {e}")

if __name__ == "__main__":
    print("="*60)
    print("ZeTheta Algorithms - S3 Bucket Setup")
    print("STRICTLY CONFIDENTIAL")
    print("="*60)
    create_s3_bucket()
