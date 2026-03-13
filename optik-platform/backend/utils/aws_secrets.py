"""
AWS Secrets Manager - Mock Implementation for Development
This is a development version that returns environment variables
instead of accessing AWS Secrets Manager.
"""

import os
from typing import Dict, Any, Optional


def get_secrets_manager() -> Dict[str, Any]:
    """Mock secrets manager for development"""
    return {
        'region': os.getenv('AWS_REGION', 'us-east-1'),
        'endpoint_url': os.getenv('AWS_ENDPOINT_URL', 'http://localhost:8000')
    }


def get_api_keys() -> Dict[str, str]:
    """Get API keys from environment variables"""
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
        'shopify_api_key': os.getenv('SHOPIFY_API_KEY', ''),
        'shopify_store_url': os.getenv('SHOPIFY_STORE_URL', ''),
    }


def get_database_credentials() -> Dict[str, str]:
    """Get database credentials from environment variables"""
    return {
        'mongodb_uri': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/optik_platform'),
        'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
    }


def get_secret(secret_name: str) -> Optional[str]:
    """Get a specific secret by name"""
    secrets_map = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'MONGODB_URI': os.getenv('MONGODB_URI'),
        'REDIS_URL': os.getenv('REDIS_URL'),
    }
    return secrets_map.get(secret_name)


# Legacy function names for backward compatibility
def get_aws_secrets() -> Dict[str, Any]:
    """Legacy function name"""
    return get_secrets_manager()


def get_aws_secret(secret_name: str) -> Optional[str]:
    """Legacy function name"""
    return get_secret(secret_name)
