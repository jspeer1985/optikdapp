"""
Secure Secrets Management Module
Handles credential retrieval from AWS Secrets Manager or environment variables
"""

import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SecretsManager:
    """Manages secure credential retrieval"""

    def __init__(self):
        self.use_aws_secrets = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        self._cache: Dict[str, Any] = {}
        
        if self.use_aws_secrets:
            try:
                import boto3
                self.client = boto3.client(
                    'secretsmanager',
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                logger.info("✅ AWS Secrets Manager initialized")
            except ImportError:
                logger.warning("⚠️ boto3 not installed, falling back to environment variables")
                self.use_aws_secrets = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize AWS Secrets Manager: {str(e)}")
                self.use_aws_secrets = False

    def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve secret from AWS Secrets Manager or environment variables
        
        Args:
            secret_name: Name of the secret (e.g., 'optik/api-keys')
            
        Returns:
            Dictionary of secret values or None if not found
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]

        if self.use_aws_secrets:
            try:
                import boto3
                response = self.client.get_secret_value(SecretId=secret_name)
                secret = json.loads(response["SecretString"])
                self._cache[secret_name] = secret
                logger.debug(f"✅ Retrieved secret from AWS: {secret_name}")
                return secret
            except Exception as e:
                logger.error(f"❌ Error retrieving secret {secret_name} from AWS: {str(e)}")
                # Fallback to environment variables
                return self._get_from_env(secret_name)
        else:
            return self._get_from_env(secret_name)

    def _get_from_env(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve secrets from environment variables"""
        
        if secret_name == "optik/database":
            return {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "optik"),
                "username": os.getenv("DB_USER", "optik"),
                "password": os.getenv("DB_PASSWORD", ""),
            }
        elif secret_name == "optik/api-keys":
            return {
                "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "stripe_secret_key": os.getenv("STRIPE_SECRET_KEY"),
                "stripe_publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
                "stripe_webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET"),
            }
        elif secret_name == "optik/blockchain":
            return {
                "solana_rpc_url": os.getenv("SOLANA_RPC_URL"),
                "solana_wallet_private_key": os.getenv("SOLANA_WALLET_PRIVATE_KEY"),
                "treasury_wallet": os.getenv("TREASURY_WALLET"),
            }
        return None


# Global instance
secrets_manager = SecretsManager()


def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    config = secrets_manager.get_secret("optik/database")
    if not config:
        raise RuntimeError("❌ Database configuration not found")
    return config


def get_api_keys() -> Dict[str, Any]:
    """Get API keys"""
    keys = secrets_manager.get_secret("optik/api-keys")
    if not keys:
        raise RuntimeError("❌ API keys not found")
    return keys


def get_blockchain_config() -> Dict[str, Any]:
    """Get blockchain configuration"""
    config = secrets_manager.get_secret("optik/blockchain")
    if not config:
        raise RuntimeError("❌ Blockchain configuration not found")
    return config


def validate_required_secrets() -> bool:
    """Validate that all required secrets are available"""
    try:
        get_api_keys()
        get_blockchain_config()
        logger.info("✅ All required secrets validated")
        return True
    except RuntimeError as e:
        logger.error(f"❌ Secret validation failed: {str(e)}")
        return False
