"""
AWS Secrets Manager Integration
Securely retrieves API keys and secrets from AWS Secrets Manager
"""

import json
import logging
from typing import Dict, Any, Optional
from functools import lru_cache
import os

logger = logging.getLogger(__name__)


class AWSSecretsManager:
    """
    AWS Secrets Manager client for secure credential retrieval
    Falls back to environment variables in development
    """

    def __init__(self):
        self.use_aws = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self._client = None
        self._cache = {}

        if self.use_aws:
            try:
                import boto3
                from botocore.exceptions import ClientError
                self.ClientError = ClientError
                self._client = boto3.client(
                    service_name='secretsmanager',
                    region_name=self.region_name
                )
                logger.info(f"AWS Secrets Manager initialized for region: {self.region_name}")
            except ImportError:
                logger.warning("boto3 not installed. Install with: pip install boto3")
                self.use_aws = False
            except Exception as e:
                logger.error(f"Failed to initialize AWS Secrets Manager: {e}")
                self.use_aws = False
        else:
            logger.info("Using environment variables (AWS Secrets disabled)")

    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a secret value from AWS Secrets Manager or environment

        Args:
            secret_name: Name of the secret to retrieve

        Returns:
            Secret value as string, or None if not found
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]

        # If AWS is enabled, try to get from Secrets Manager
        if self.use_aws and self._client:
            try:
                response = self._client.get_secret_value(SecretId=secret_name)

                # Secrets can be stored as string or binary
                if 'SecretString' in response:
                    secret = response['SecretString']
                else:
                    import base64
                    secret = base64.b64decode(response['SecretBinary']).decode('utf-8')

                self._cache[secret_name] = secret
                logger.info(f"Retrieved secret from AWS: {secret_name}")
                return secret

            except self.ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    logger.warning(f"Secret not found in AWS: {secret_name}")
                elif error_code == 'InvalidRequestException':
                    logger.error(f"Invalid request for secret: {secret_name}")
                elif error_code == 'InvalidParameterException':
                    logger.error(f"Invalid parameter for secret: {secret_name}")
                else:
                    logger.error(f"Error retrieving secret {secret_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error retrieving secret {secret_name}: {e}")

        # Fallback to environment variable
        env_value = os.getenv(secret_name)
        if env_value:
            logger.debug(f"Retrieved secret from environment: {secret_name}")
            self._cache[secret_name] = env_value
            return env_value

        logger.warning(f"Secret not found: {secret_name}")
        return None

    def get_secret_json(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a JSON secret and parse it

        Args:
            secret_name: Name of the JSON secret

        Returns:
            Parsed JSON as dictionary, or None if not found/invalid
        """
        secret_string = self.get_secret(secret_name)
        if not secret_string:
            return None

        try:
            return json.loads(secret_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON secret {secret_name}: {e}")
            return None

    def get_database_credentials(self) -> Dict[str, str]:
        """
        Get database credentials from AWS Secrets or environment

        Returns:
            Dictionary with database connection info
        """
        # Try to get from AWS as JSON secret
        if self.use_aws:
            db_secret = self.get_secret_json("optik/database")
            if db_secret:
                return db_secret

        # Fallback to environment variables
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "optik"),
            "username": os.getenv("DB_USER", "optik"),
            "password": os.getenv("DB_PASSWORD", ""),
            "url": os.getenv("DATABASE_URL", "sqlite:///optik.db")
        }

    def get_api_keys(self) -> Dict[str, str]:
        """
        Get all API keys from AWS Secrets or environment

        Returns:
            Dictionary with all API keys
        """
        # Try to get from AWS as JSON secret
        if self.use_aws:
            api_keys = self.get_secret_json("optik/api-keys")
            if api_keys:
                return api_keys

        # Fallback to environment variables
        return {
            "anthropic_api_key": self.get_secret("ANTHROPIC_API_KEY") or "",
            "openai_api_key": self.get_secret("OPENAI_API_KEY") or "",
            "stripe_secret_key": self.get_secret("STRIPE_SECRET_KEY") or "",
            "stripe_webhook_secret": self.get_secret("STRIPE_WEBHOOK_SECRET") or "",
            "pinata_api_key": self.get_secret("PINATA_API_KEY") or "",
            "pinata_secret_key": self.get_secret("PINATA_SECRET_KEY") or "",
            "pinata_jwt_secret": self.get_secret("PINATA_JWT_SECRET") or "",
        }

    def get_blockchain_config(self) -> Dict[str, str]:
        """
        Get blockchain configuration from AWS Secrets or environment

        Returns:
            Dictionary with blockchain config
        """
        # Try to get from AWS as JSON secret
        if self.use_aws:
            blockchain_config = self.get_secret_json("optik/blockchain")
            if blockchain_config:
                return blockchain_config

        # Fallback to environment variables
        return {
            "solana_rpc_url": self.get_secret("SOLANA_RPC_URL") or "https://api.devnet.solana.com",
            "solana_wallet_private_key": self.get_secret("SOLANA_WALLET_PRIVATE_KEY") or "",
            "treasury_wallet": self.get_secret("TREASURY_WALLET") or "",
            "platform_fee_percentage": self.get_secret("PLATFORM_FEE_PERCENTAGE") or "3",
        }

    def refresh_cache(self):
        """Clear the cache to force fresh retrieval"""
        self._cache.clear()
        self.get_secret.cache_clear()
        logger.info("Secrets cache cleared")


# Global singleton instance
_secrets_manager = None


def get_secrets_manager() -> AWSSecretsManager:
    """
    Get or create the global secrets manager instance

    Returns:
        AWSSecretsManager singleton instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = AWSSecretsManager()
    return _secrets_manager


# Convenience functions for common secrets
def get_secret(name: str) -> Optional[str]:
    """Get a secret by name"""
    return get_secrets_manager().get_secret(name)


def get_api_keys() -> Dict[str, str]:
    """Get all API keys"""
    return get_secrets_manager().get_api_keys()


def get_database_credentials() -> Dict[str, str]:
    """Get database credentials"""
    return get_secrets_manager().get_database_credentials()


def get_blockchain_config() -> Dict[str, str]:
    """Get blockchain configuration"""
    return get_secrets_manager().get_blockchain_config()
