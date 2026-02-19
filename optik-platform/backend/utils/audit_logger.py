"""
Comprehensive Audit Logging System
Tracks all important actions for compliance and security
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class AuditAction(Enum):
    """Types of auditable actions"""
    PAYMENT_CREATED = "payment_created"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    REFUND_ISSUED = "refund_issued"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    SETTINGS_CHANGED = "settings_changed"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    MERCHANT_REGISTERED = "merchant_registered"
    MERCHANT_UPDATED = "merchant_updated"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    SECURITY_EVENT = "security_event"
    ADMIN_ACTION = "admin_action"
    ERROR_EVENT = "error_event"
    BLOCKCHAIN_TX = "blockchain_transaction"
    WEBHOOK_RECEIVED = "webhook_received"


class AuditLogger:
    """Comprehensive audit logging"""

    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # File handler for audit logs
        file_handler = logging.FileHandler("logs/audit.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter(
            '%(message)s'
        )
        file_handler.setFormatter(formatter)

        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "success",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log an audit event
        
        Args:
            action: Type of action (AuditAction enum)
            user_id: User who performed the action
            merchant_id: Associated merchant
            resource_id: Resource being acted upon
            resource_type: Type of resource
            changes: What was changed
            status: success/failure/pending
            ip_address: Client IP address
            user_agent: User agent string
            metadata: Additional metadata
            error: Error message if failed
            
        Returns:
            Dictionary of audit entry for additional processing
        """

        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action.value,
            "user_id": user_id,
            "merchant_id": merchant_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "changes": changes or {},
            "status": status,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "metadata": metadata or {},
            "error": error,
        }

        # Log as JSON for easy parsing
        try:
            self.logger.info(json.dumps(audit_entry))
            print(f"✅ Audit logged: {action.value} ({status})")
        except Exception as e:
            print(f"❌ Failed to log audit event: {str(e)}")

        return audit_entry

    def log_payment(
        self,
        action: AuditAction,
        payment_id: str,
        user_id: str,
        amount: float,
        currency: str,
        status: str,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log payment-related action"""
        return self.log(
            action=action,
            user_id=user_id,
            resource_id=payment_id,
            resource_type="payment",
            changes={
                "amount": amount,
                "currency": currency,
                "status": status,
            },
            ip_address=ip_address,
            metadata=metadata or {},
        )

    def log_authentication(
        self,
        action: AuditAction,
        user_id: Optional[str],
        status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log authentication events"""
        return self.log(
            action=action,
            user_id=user_id,
            resource_type="authentication",
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"reason": reason} if reason else {},
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log security events"""
        return self.log(
            action=AuditAction.SECURITY_EVENT,
            user_id=user_id,
            status="alert",
            ip_address=ip_address,
            metadata={
                "event_type": event_type,
                "severity": severity,
                "description": description,
                **(metadata or {}),
            },
        )

    def log_blockchain_transaction(
        self,
        tx_hash: str,
        network: str,
        user_id: Optional[str],
        amount: Optional[float] = None,
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log blockchain transactions"""
        return self.log(
            action=AuditAction.BLOCKCHAIN_TX,
            user_id=user_id,
            resource_id=tx_hash,
            resource_type="blockchain",
            status=status,
            metadata={
                "network": network,
                "amount": amount,
                **(metadata or {}),
            },
        )

    def log_webhook(
        self,
        source: str,
        event_type: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log webhook events"""
        return self.log(
            action=AuditAction.WEBHOOK_RECEIVED,
            resource_type="webhook",
            status=status,
            metadata={
                "source": source,
                "event_type": event_type,
                **(metadata or {}),
            },
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log error events"""
        return self.log(
            action=AuditAction.ERROR_EVENT,
            user_id=user_id,
            status="error",
            ip_address=ip_address,
            error=error_message,
            metadata={
                "error_type": error_type,
                **(metadata or {}),
            },
        )


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    return audit_logger
