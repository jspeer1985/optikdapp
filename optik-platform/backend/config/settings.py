"""
Security Configuration Module
Centralizes all security settings and initializations
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration settings"""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Secrets Management
    USE_AWS_SECRETS = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    # CORS Settings
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:3000")
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_STRICT_ENDPOINTS = {
        "/api/v1/auth/login": 5,
        "/api/v1/auth/register": 3,
        "/api/v1/payments/create": 10,
        "/api/v1/webhooks": 100,
    }

    # JWT Security
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")

    # Security Headers
    SECURITY_HEADERS_ENABLED = True
    HSTS_ENABLED = ENVIRONMENT == "production"
    HSTS_MAX_AGE = 31536000  # 1 year
    CSP_ENABLED = True

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    AUDIT_LOGGING_ENABLED = True
    AUDIT_LOG_FILE = "logs/audit.log"

    # API Security
    API_KEY_ROTATION_DAYS = 90
    API_RATE_LIMIT_ENABLED = True
    ENABLE_SWAGGER_UI = DEBUG

    @classmethod
    def validate(cls) -> bool:
        """Validate security configuration"""
        errors = []

        # Check for exposed secrets
        if not cls.USE_AWS_SECRETS and cls.ENVIRONMENT == "production":
            errors.append("❌ AWS Secrets Manager not enabled in production!")

        if cls.JWT_SECRET == "change-me-in-production" and cls.ENVIRONMENT == "production":
            errors.append("❌ JWT_SECRET is using default value in production!")

        if cls.DEBUG and cls.ENVIRONMENT == "production":
            errors.append("⚠️ DEBUG mode is enabled in production!")

        if cls.ENABLE_SWAGGER_UI and cls.ENVIRONMENT == "production":
            errors.append("⚠️ Swagger UI is enabled in production!")

        if errors:
            for error in errors:
                logger.warning(error)
            return False

        logger.info("✅ Security configuration validated successfully")
        return True

    @classmethod
    def get_config_dict(cls) -> dict:
        """Get configuration as dictionary"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "use_aws_secrets": cls.USE_AWS_SECRETS,
            "rate_limit_enabled": cls.RATE_LIMIT_ENABLED,
            "security_headers_enabled": cls.SECURITY_HEADERS_ENABLED,
            "audit_logging_enabled": cls.AUDIT_LOGGING_ENABLED,
        }


def get_settings():
    """Get settings instance"""
    return SecurityConfig()


# Global settings instance
settings = SecurityConfig()
