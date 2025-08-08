import os
import requests
import json
import logging

logger = logging.getLogger(__name__)

def get_doppler_secret(key, default=None):
    """Get secret from Doppler API"""
    token = os.environ.get('DOPPLER_TOKEN')
    if not token:
        return default
    
    try:
        response = requests.get(
            'https://api.doppler.com/v3/configs/config/secrets/download',
            headers={'Authorization': f'Bearer {token}'},
            params={'format': 'json'}
        )
        response.raise_for_status()
        secrets = response.json()
        return secrets.get(key, default)
    except Exception as e:
        logger.error(f"Error getting Doppler secret {key}: {e}")
        return default

class Config:
    # Supabase PostgreSQL connection with SSL
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return get_doppler_secret('DATABASE_URL', 
            'postgresql://postgres.khewnzogdzolwyflgazn:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require'
        )
    
    @property
    def SECRET_KEY(self):
        return get_doppler_secret('API_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS Lambda + Supabase optimized settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,  # 5min for Lambda lifecycle
        'pool_size': 1,       # Single connection for Lambda
        'max_overflow': 0,    # No overflow in serverless
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'score_handler_lambda',
            'sslmode': 'require'  # Force SSL connection
        }
    }
    