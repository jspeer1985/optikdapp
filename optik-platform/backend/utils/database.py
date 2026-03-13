from dotenv import load_dotenv
load_dotenv()
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import databases
import sqlalchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Float,
    DateTime,
    JSON,
    Integer,
    Boolean,
    Text,
    func,
)
from utils.env import allow_demo_data

logger = logging.getLogger(__name__)

# Define database URL — must be set via environment variable, no hardcoded fallback
_RAW_DB_URL = os.getenv("DATABASE_URL")
if not _RAW_DB_URL:
    raise EnvironmentError(
        "DATABASE_URL environment variable is required but not set. "
        "Example: postgresql://user:password@localhost:5432/optik"
    )

# Allow non-Postgres URLs (like SQLite for tests) if needed, but default to Postgres
if _RAW_DB_URL.startswith("mongodb"):
    raise EnvironmentError(
        "DATABASE_URL points to MongoDB, but this module requires a PostgreSQL or SQLite URL."
    )

# Handle SQLite vs PostgreSQL URL formats
if "sqlite" in _RAW_DB_URL:
    if "aiosqlite" not in _RAW_DB_URL:
        ASYNC_DATABASE_URL = _RAW_DB_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
    else:
        ASYNC_DATABASE_URL = _RAW_DB_URL
    SYNC_DATABASE_URL = _RAW_DB_URL.replace("+aiosqlite", "")
else:
    if "asyncpg" not in _RAW_DB_URL:
        ASYNC_DATABASE_URL = _RAW_DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        ASYNC_DATABASE_URL = _RAW_DB_URL

    SYNC_DATABASE_URL = _RAW_DB_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

DATABASE_URL = ASYNC_DATABASE_URL

metadata = MetaData()

# ---------------- Auth & User Tables ----------------
users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String, unique=True, index=True, nullable=True),
    Column("wallet_address", String, unique=True, index=True, nullable=True),
    Column("role", String, default="merchant"),
    Column("status", String, default="active"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("refresh_token_hash", String),
    Column("expires_at", DateTime),
    Column("revoked_at", DateTime, nullable=True),
    Column("ip_address", String, nullable=True),
    Column("user_agent", Text, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

wallet_nonces = Table(
    "wallet_nonces",
    metadata,
    Column("id", String, primary_key=True),
    Column("wallet_address", String, index=True),
    Column("nonce", String, index=True),
    Column("origin", String, nullable=True),
    Column("expires_at", DateTime),
    Column("used_at", DateTime, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

magic_links = Table(
    "magic_links",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("token_hash", String, index=True),
    Column("expires_at", DateTime),
    Column("used_at", DateTime, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

api_keys = Table(
    "api_keys",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("name", String, nullable=True),
    Column("key_hash", String, unique=True, index=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("last_used_at", DateTime, nullable=True),
)

merchants = Table(
    "merchants",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, unique=True, index=True),
    Column("tier", String, default="basic"),
    Column("status", String, default="pending"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

ledger_entries = Table(
    "ledger_entries",
    metadata,
    Column("id", String, primary_key=True),
    Column("order_id", String, index=True),
    Column("merchant_id", String, index=True),
    Column("transaction_type", String),
    Column("status", String),
    Column("gross_amount", Integer),
    Column("platform_fee", Integer),
    Column("merchant_payout", Integer),
    Column("currency", String),
    Column("solana_signature", String, nullable=True),
    Column("metadata", JSON, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

webhook_events = Table(
    "webhook_events",
    metadata,
    Column("id", String, primary_key=True),
    Column("provider", String, index=True),
    Column("event_id", String, index=True),
    Column("payload", JSON, nullable=True),
    Column("status", String, default="received"),
    Column("received_at", DateTime, default=datetime.utcnow),
    Column("processed_at", DateTime, nullable=True),
)

# ---------------- Core Domain Tables ----------------
jobs = Table(
    "jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String),
    Column("store_name", String, nullable=True),
    Column("store_url", String),
    Column("platform", String),
    Column("tier", String),
    Column("status", String),
    Column("progress", Integer, default=0),
    Column("message", String),
    Column("dapp_url", String, nullable=True),
    Column("deployment_id", String, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
    Column("error", String, nullable=True),
    Column("deployment_config", JSON, nullable=True),
)

webhook_configs = Table(
    "webhook_configs",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("config", JSON),
    Column("created_at", DateTime, default=datetime.utcnow),
)

nft_assets = Table(
    "nft_assets",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("name", String),
    Column("symbol", String),
    Column("description", Text, nullable=True),
    Column("image_url", String),
    Column("metadata_url", String),
    Column("seller_fee_basis_points", Integer),
    Column("backing_amount", Float, default=0.0),
    Column("status", String, default="prepared"),
    Column("created_at", DateTime, default=datetime.utcnow),
)

marketing_requests = Table(
    "marketing_requests",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("request_type", String),
    Column("payload", JSON, nullable=True),
    Column("status", String, default="queued"),
    Column("created_at", DateTime, default=datetime.utcnow),
)

liquidity_requests = Table(
    "liquidity_requests",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("amount_sol", Float),
    Column("status", String, default="pending"),
    Column("created_at", DateTime, default=datetime.utcnow),
)

security_events = Table(
    "security_events",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("message", Text),
    Column("created_at", DateTime, default=datetime.utcnow),
)

ip_whitelist = Table(
    "ip_whitelist",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("ip", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)

security_actions = Table(
    "security_actions",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("action", String),
    Column("status", String, default="requested"),
    Column("created_at", DateTime, default=datetime.utcnow),
)


user_agreements = Table(
    "user_agreements",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("agreement_version", String),
    Column("accepted_at", DateTime, default=datetime.utcnow),
    Column("ip_address", String, nullable=True),
    Column("user_agent", Text, nullable=True),
)

onboarding_payments = Table(
    "onboarding_payments",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("amount_cents", Integer),
    Column("currency", String),
    Column("status", String, default="pending"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

proofs = Table(
    "proofs",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("job_id", String, index=True, nullable=True),
    Column("workflow_id", String, nullable=True),
    Column("step_id", String, nullable=True),
    Column("file_path", String, nullable=True),
    Column("owner_agent", String, nullable=True),
    Column("proof_type", String, default="workflow"),
    Column("status", String, default="completed"),
    Column("details", JSON, nullable=True),
    Column("artifacts", JSON, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

conversions = Table(
    "conversions",
    metadata,
    Column("job_id", String, primary_key=True),
    Column("web3_store_data", JSON),
    Column("nft_data", JSON),
    Column("created_at", DateTime, default=datetime.utcnow),
)

deployments = Table(
    "deployments",
    metadata,
    Column("job_id", String, primary_key=True),
    Column("tx_hash", String),
    Column("merchant_pda", String),
    Column("network", String),
    Column("dapp_url", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)

products_table = Table(
    "products",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("name", String),
    Column("description", String, nullable=True),
    Column("supply", String),
    Column("sold", Integer, default=0),
    Column("price", String),
    Column("status", String),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)

integrations_table = Table(
    "integrations",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, index=True),
    Column("name", String),
    Column("detail", String),
    Column("status", String),
    Column("icon", String),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow),
)


class DatabaseManager:
    """
    Manages connections to the PostgreSQL database via `databases` (async) and `sqlalchemy` (schema).
    """
    def __init__(self):
        self.database = databases.Database(ASYNC_DATABASE_URL)
        self.engine = create_engine(SYNC_DATABASE_URL)

    async def connect(self):
        logger.info("Connecting to database...")
        try:
            await self.database.connect()
            metadata.create_all(self.engine)
            await self._seed_demo_data()
            logger.info("Database connected and schema verified.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            pass

    async def disconnect(self):
        logger.info("Disconnecting from database...")
        try:
            if self.database.is_connected:
                await self.database.disconnect()
        except Exception as e:
            logger.warning(f"Database disconnect issue (non-critical): {e}")

    async def check_connection(self) -> bool:
        try:
            return self.database.is_connected
        except Exception:
            return False

    async def _seed_demo_data(self):
        if os.getenv("SEED_DEMO_DATA", "false").lower() != "true":
            return
        if not allow_demo_data():
            logger.info("Demo data seeding is disabled outside non-production environments.")
            return

        demo_email = os.getenv("DEMO_USER_EMAIL", "merchant@example.com")
        demo_user = await self.get_user_by_email(demo_email)
        if not demo_user:
            demo_user = await self.create_user(email=demo_email, wallet_address=None)

        demo_user_id = demo_user["id"]

        try:
            count = await self.database.fetch_val(
                sqlalchemy.select(func.count())
                .select_from(products_table)
                .where(products_table.c.user_id == demo_user_id)
            )
        except Exception:
            count = None

        if count == 0:
            default_products = [
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Genesis Hoodie", "supply": "100", "sold": 45, "price": "0.5 SOL", "status": "Live", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Founder Cap", "supply": "50", "sold": 50, "price": "1.2 SOL", "status": "Sold Out", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Digital Badge", "supply": "Unlimited", "sold": 1240, "price": "0.1 SOL", "status": "Live", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
            ]
            await self.database.execute_many(query=products_table.insert(), values=default_products)

        try:
            count_int = await self.database.fetch_val(
                sqlalchemy.select(func.count())
                .select_from(integrations_table)
                .where(integrations_table.c.user_id == demo_user_id)
            )
        except Exception:
            count_int = None

        if count_int == 0:
            default_integrations = [
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Shopify Sync", "detail": "Import products & sync inventory with Shopify store.", "status": "Connected", "icon": "🛍️", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "WooCommerce", "detail": "Direct bridge to your WordPress storefront.", "status": "Available", "icon": "🛒", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Stripe Connect", "detail": "Fiat-to-Crypto settlement rails.", "status": "Connected", "icon": "💳", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"id": str(uuid.uuid4()), "user_id": demo_user_id, "name": "Discord Bot", "detail": "Automated sales alerts & NFT role verification.", "status": "Incomplete", "icon": "💬", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
            ]
            await self.database.execute_many(query=integrations_table.insert(), values=default_integrations)

    # ---------------- Users ----------------
    async def create_user(self, email: Optional[str], wallet_address: Optional[str], role: str = "merchant") -> Dict[str, Any]:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        query = users.insert().values(
            id=user_id,
            email=email,
            wallet_address=wallet_address,
            role=role,
            status="active",
            created_at=now,
            updated_at=now,
        )
        await self.database.execute(query)
        return {
            "id": user_id,
            "email": email,
            "wallet_address": wallet_address,
            "role": role,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(users.select().where(users.c.id == user_id))
        return dict(result) if result else None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(users.select().where(users.c.email == email))
        return dict(result) if result else None

    async def get_user_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(users.select().where(users.c.wallet_address == wallet_address))
        return dict(result) if result else None

    async def update_user(self, user_id: str, updates: Dict[str, Any]):
        updates["updated_at"] = datetime.utcnow()
        query = users.update().where(users.c.id == user_id).values(**updates)
        await self.database.execute(query)

    # ---------------- Sessions ----------------
    async def create_session(self, user_id: str, refresh_token_hash: str, expires_at: datetime, ip_address: str | None, user_agent: str | None, session_id: str | None = None) -> str:
        session_id = session_id or f"sess_{uuid.uuid4().hex}"
        query = sessions.insert().values(
            id=session_id,
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.database.execute(query)
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(sessions.select().where(sessions.c.id == session_id))
        return dict(result) if result else None

    async def update_session_refresh(self, session_id: str, refresh_token_hash: str, expires_at: datetime):
        query = sessions.update().where(sessions.c.id == session_id).values(
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
        await self.database.execute(query)

    async def revoke_session(self, session_id: str):
        query = sessions.update().where(sessions.c.id == session_id).values(revoked_at=datetime.utcnow())
        await self.database.execute(query)

    async def revoke_user_sessions(self, user_id: str):
        query = sessions.update().where(sessions.c.user_id == user_id).values(revoked_at=datetime.utcnow())
        await self.database.execute(query)

    # ---------------- Wallet Nonces ----------------
    async def create_wallet_nonce(self, wallet_address: str, nonce: str, expires_at: datetime, origin: Optional[str]) -> Dict[str, Any]:
        nonce_id = f"nonce_{uuid.uuid4().hex}"
        query = wallet_nonces.insert().values(
            id=nonce_id,
            wallet_address=wallet_address,
            nonce=nonce,
            origin=origin,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        await self.database.execute(query)
        return {
            "id": nonce_id,
            "wallet_address": wallet_address,
            "nonce": nonce,
            "origin": origin,
            "expires_at": expires_at,
        }

    async def get_wallet_nonce(self, wallet_address: str, nonce: str) -> Optional[Dict[str, Any]]:
        query = (
            wallet_nonces.select()
            .where(wallet_nonces.c.wallet_address == wallet_address)
            .where(wallet_nonces.c.nonce == nonce)
            .where(wallet_nonces.c.used_at.is_(None))
            .order_by(wallet_nonces.c.created_at.desc())
        )
        result = await self.database.fetch_one(query)
        return dict(result) if result else None

    async def mark_wallet_nonce_used(self, nonce_id: str):
        query = wallet_nonces.update().where(wallet_nonces.c.id == nonce_id).values(used_at=datetime.utcnow())
        await self.database.execute(query)

    # ---------------- Magic Links ----------------
    async def create_magic_link(self, user_id: str, token_hash: str, expires_at: datetime) -> str:
        link_id = f"mlink_{uuid.uuid4().hex}"
        query = magic_links.insert().values(
            id=link_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        await self.database.execute(query)
        return link_id

    async def get_magic_link(self, token_hash: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(
            magic_links.select()
            .where(magic_links.c.token_hash == token_hash)
            .where(magic_links.c.used_at.is_(None))
        )
        return dict(result) if result else None

    async def mark_magic_link_used(self, link_id: str):
        query = magic_links.update().where(magic_links.c.id == link_id).values(used_at=datetime.utcnow())
        await self.database.execute(query)

    # ---------------- API Keys ----------------
    async def get_api_key(self, key_hash: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(api_keys.select().where(api_keys.c.key_hash == key_hash))
        return dict(result) if result else None

    async def create_api_key(self, user_id: str, key_hash: str, name: Optional[str]):
        key_id = f"key_{uuid.uuid4().hex}"
        query = api_keys.insert().values(
            id=key_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            created_at=datetime.utcnow(),
        )
        await self.database.execute(query)
        return key_id

    # ---------------- Merchants ----------------
    async def get_merchant_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(merchants.select().where(merchants.c.user_id == user_id))
        return dict(result) if result else None

    async def get_merchant(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(merchants.select().where(merchants.c.id == merchant_id))
        return dict(result) if result else None

        return dict(result) if result else None

        existing = await self.get_merchant_by_user(user_id)
        now = datetime.utcnow()
        if existing:
            updates = {
                "tier": tier,
                "status": status,
                "updated_at": now,
            }
            query = merchants.update().where(merchants.c.user_id == user_id).values(**updates)
            await self.database.execute(query)
            return {**existing, **updates}

        merchant_id = f"m_{uuid.uuid4().hex[:10]}"
        query = merchants.insert().values(
            id=merchant_id,
            user_id=user_id,
            tier=tier,
            status=status,
            created_at=now,
            updated_at=now,
        )
        await self.database.execute(query)
        return {
            "id": merchant_id,
            "user_id": user_id,
            "tier": tier,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

    # ---------------- Ledger ----------------
    async def record_ledger_entry(self, entry: Dict[str, Any]) -> str:
        entry_id = entry.get("id") or f"led_{uuid.uuid4().hex}"
        data = {
            "id": entry_id,
            "order_id": entry.get("order_id"),
            "merchant_id": entry.get("merchant_id"),
            "transaction_type": entry.get("transaction_type"),
            "status": entry.get("status"),
            "gross_amount": entry.get("gross_amount"),
            "platform_fee": entry.get("platform_fee"),
            "merchant_payout": entry.get("merchant_payout"),
            "currency": entry.get("currency", "usd"),
            "solana_signature": entry.get("solana_signature"),
            "metadata": entry.get("metadata"),
            "created_at": entry.get("created_at") or datetime.utcnow(),
        }
        await self.database.execute(ledger_entries.insert().values(**data))
        return entry_id

    async def get_ledger_entries(self, merchant_id: str) -> List[Dict[str, Any]]:
        rows = await self.database.fetch_all(
            ledger_entries.select().where(ledger_entries.c.merchant_id == merchant_id).order_by(ledger_entries.c.created_at.desc())
        )
        return [dict(r) for r in rows]

    # ---------------- Webhook Events ----------------
    async def get_webhook_event(self, provider: str, event_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(
            webhook_events.select().where(webhook_events.c.provider == provider).where(webhook_events.c.event_id == event_id)
        )
        return dict(result) if result else None

    async def record_webhook_event(self, provider: str, event_id: str, payload: Dict[str, Any]) -> str:
        event_db_id = f"wh_{uuid.uuid4().hex}"
        await self.database.execute(
            webhook_events.insert().values(
                id=event_db_id,
                provider=provider,
                event_id=event_id,
                payload=payload,
                status="received",
                received_at=datetime.utcnow(),
            )
        )
        return event_db_id

    async def mark_webhook_processed(self, provider: str, event_id: str, status: str = "processed"):
        await self.database.execute(
            webhook_events.update()
            .where(webhook_events.c.provider == provider)
            .where(webhook_events.c.event_id == event_id)
            .values(status=status, processed_at=datetime.utcnow())
        )

    # ---------------- Conversion Jobs ----------------
    async def create_conversion_job(self, user_id: str, store_url: str, platform: str, tier: str, email: str) -> str:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        query = jobs.insert().values(
            id=job_id,
            user_id=user_id,
            store_url=store_url,
            platform=platform,
            tier=tier,
            status="pending",
            progress=0,
            message="Job created",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await self.database.execute(query)
        logger.info(f"Created job {job_id} in database")
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(jobs.select().where(jobs.c.id == job_id))
        return dict(result) if result else None

    async def get_job(self, job_id: str) -> Any:
        result = await self.database.fetch_one(jobs.select().where(jobs.c.id == job_id))
        if result:
            class JobWrapper:
                def __init__(self, data):
                    self.id = data["id"]
                    self.user_id = data["user_id"]
                    self.status = data["status"]
                    self.tier = data["tier"]
            return JobWrapper(dict(result))
        return None

    async def update_job_status(self, job_id: str, status: str, progress: Optional[int] = None, message: Optional[str] = None, error: Optional[str] = None, dapp_url: Optional[str] = None):
        updates = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }
        if progress is not None:
            updates["progress"] = progress
        if message is not None:
            updates["message"] = message
        if error is not None:
            updates["error"] = error
        if dapp_url is not None:
            updates["dapp_url"] = dapp_url
        query = jobs.update().where(jobs.c.id == job_id).values(**updates)
        await self.database.execute(query)
        logger.info(f"Updated job {job_id} to {status}")

    async def save_conversion_result(self, job_id: str, web3_store: Dict, nft_data: List):
        query = conversions.insert().values(
            job_id=job_id,
            web3_store_data=web3_store,
            nft_data=nft_data,
            created_at=datetime.utcnow(),
        )
        await self.database.execute(query)
        logger.info(f"Saved conversion result for {job_id}")

    async def get_conversion_data(self, job_id: str) -> Dict:
        result = await self.database.fetch_one(conversions.select().where(conversions.c.job_id == job_id))
        if result:
            return dict(result)["web3_store_data"]
        return {}

    async def update_deployment_config(self, job_id: str, config: Dict):
        query = jobs.update().where(jobs.c.id == job_id).values(
            deployment_config=config,
            updated_at=datetime.utcnow(),
        )
        await self.database.execute(query)

    async def update_deployment_result(self, job_id: str, result: Dict):
        query = deployments.insert().values(
            job_id=job_id,
            tx_hash=result.get("tx_hash", ""),
            merchant_pda=result.get("merchant_pda", {}).get("merchant", "") if isinstance(result.get("merchant_pda"), dict) else str(result.get("merchant_pda", "")),
            network=result.get("network", "devnet"),
            dapp_url=result.get("dapp_url", ""),
            created_at=datetime.utcnow(),
        )
        try:
            await self.database.execute(query)
        except Exception as e:
            logger.error(f"Failed to record deployment: {e}")

        await self.update_job_status(job_id, "deployed", dapp_url=result.get("dapp_url"))
        logger.info(f"Updated deployment result for {job_id}")

    async def get_conversion_count(self) -> int:
        try:
            result = await self.database.fetch_val("SELECT COUNT(*) FROM jobs WHERE status IN ('completed', 'deployed')")
            return result or 0
        except Exception:
            return 0

    async def get_total_revenue(self) -> float:
        try:
            result = await self.database.fetch_val("SELECT COALESCE(SUM(gross_amount), 0) FROM ledger_entries")
            return float(result or 0) / 100
        except Exception:
            return 0.0

    async def save_webhook_config(self, user_id: str, config: Dict):
        await self.database.execute(
            webhook_configs.insert().values(
                id=f"whcfg_{uuid.uuid4().hex}",
                user_id=user_id,
                config=config,
                created_at=datetime.utcnow(),
            )
        )

    async def list_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        rows = await self.database.fetch_all(
            jobs.select().where(jobs.c.user_id == user_id).order_by(jobs.c.created_at.desc())
        )
        return [dict(r) for r in rows]

    # ---------------- Products CRUD ----------------
    async def get_products(self, user_id: str) -> List[Dict]:
        results = await self.database.fetch_all(products_table.select().where(products_table.c.user_id == user_id))
        return [dict(r) for r in results]

    async def create_product(self, product_data: Dict) -> str:
        data = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **product_data,
        }
        await self.database.execute(products_table.insert().values(**data))
        return data["id"]

    async def update_product(self, product_id: str, user_id: str, updates: Dict):
        updates["updated_at"] = datetime.utcnow()
        query = (
            products_table.update()
            .where(products_table.c.id == product_id)
            .where(products_table.c.user_id == user_id)
            .values(**updates)
        )
        await self.database.execute(query)

    async def delete_product(self, product_id: str, user_id: str):
        query = products_table.delete().where(products_table.c.id == product_id).where(products_table.c.user_id == user_id)
        await self.database.execute(query)

    # ---------------- Integrations CRUD ----------------
    async def get_integrations(self, user_id: str) -> List[Dict]:
        results = await self.database.fetch_all(integrations_table.select().where(integrations_table.c.user_id == user_id))
        return [dict(r) for r in results]

    async def update_integration(self, integration_id: str, user_id: str, updates: Dict):
        updates["updated_at"] = datetime.utcnow()
        query = (
            integrations_table.update()
            .where(integrations_table.c.id == integration_id)
            .where(integrations_table.c.user_id == user_id)
            .values(**updates)
        )
        await self.database.execute(query)

    # ---------------- Jobs & Dapps ----------------
    async def update_job_store_name(self, job_id: str, store_name: str):
        query = jobs.update().where(jobs.c.id == job_id).values(store_name=store_name, updated_at=datetime.utcnow())
        await self.database.execute(query)

    async def get_conversion_record(self, job_id: str) -> Optional[Dict[str, Any]]:
        result = await self.database.fetch_one(conversions.select().where(conversions.c.job_id == job_id))
        return dict(result) if result else None

    async def list_deployed_dapps(self, user_id: str) -> List[Dict[str, Any]]:
        rows = await self.database.fetch_all(
            jobs.select()
            .where(jobs.c.user_id == user_id)
            .where(jobs.c.status.in_(["deployed"]))
            .order_by(jobs.c.updated_at.desc())
        )
        return [dict(r) for r in rows]

    async def list_public_dapps(self, limit: int = 20) -> List[Dict[str, Any]]:
        rows = await self.database.fetch_all(
            jobs.select()
            .where(jobs.c.status.in_(["deployed"]))
            .order_by(jobs.c.updated_at.desc())
            .limit(limit)
        )
        return [dict(r) for r in rows]

    async def get_latest_dapp_for_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = await self.database.fetch_one(
            jobs.select()
            .where(jobs.c.user_id == user_id)
            .where(jobs.c.status.in_(["deployed"]))
            .order_by(jobs.c.updated_at.desc())
        )
        return dict(row) if row else None

    # ---------------- NFT Assets ----------------
    async def create_nft_asset(self, user_id: str, asset: Dict[str, Any]) -> str:
        asset_id = f"nft_{uuid.uuid4().hex}"
        data = {
            "id": asset_id,
            "user_id": user_id,
            "name": asset["name"],
            "symbol": asset["symbol"],
            "description": asset.get("description"),
            "image_url": asset["image_url"],
            "metadata_url": asset["metadata_url"],
            "seller_fee_basis_points": asset["seller_fee_basis_points"],
            "backing_amount": asset.get("backing_amount", 0.0),
            "status": asset.get("status", "prepared"),
            "created_at": datetime.utcnow(),
        }
        await self.database.execute(nft_assets.insert().values(**data))
        return asset_id

    # ---------------- Marketing Requests ----------------
    async def create_marketing_request(self, user_id: str, request_type: str, payload: Dict[str, Any]) -> str:
        request_id = f"mrk_{uuid.uuid4().hex}"
        await self.database.execute(
            marketing_requests.insert().values(
                id=request_id,
                user_id=user_id,
                request_type=request_type,
                payload=payload,
                status="queued",
                created_at=datetime.utcnow(),
            )
        )
        return request_id

    async def list_marketing_logs(self, user_id: str, limit: int = 20) -> List[str]:
        rows = await self.database.fetch_all(
            marketing_requests.select()
            .where(marketing_requests.c.user_id == user_id)
            .order_by(marketing_requests.c.created_at.desc())
            .limit(limit)
        )
        logs = []
        for row in rows:
            payload = row["payload"] or {}
            logs.append(f"{row['created_at']}: {row['request_type']} - {payload}")
        return logs

    # ---------------- Liquidity Requests ----------------
    async def create_liquidity_request(self, user_id: str, amount_sol: float) -> str:
        request_id = f"liq_{uuid.uuid4().hex}"
        await self.database.execute(
            liquidity_requests.insert().values(
                id=request_id,
                user_id=user_id,
                amount_sol=amount_sol,
                status="pending",
                created_at=datetime.utcnow(),
            )
        )
        return request_id

    async def get_liquidity_summary(self, user_id: str) -> Dict[str, Any]:
        rows = await self.database.fetch_all(
            liquidity_requests.select().where(liquidity_requests.c.user_id == user_id)
        )
        approved_amount = sum(r["amount_sol"] for r in rows if r["status"] == "approved")
        sol_usd = float(os.getenv("SOL_USD_PRICE", "0") or 0)
        backed_usd = approved_amount * sol_usd if sol_usd else 0.0
        return {
            "backed_amount": approved_amount,
            "backed_usd": backed_usd,
            "apy": float(os.getenv("LIQUIDITY_APY", "0") or 0),
            "stability_ratio": float(os.getenv("LIQUIDITY_STABILITY_RATIO", "0") or 0),
        }

    # ---------------- Security ----------------
    async def record_security_event(self, user_id: str, message: str) -> str:
        event_id = f"sec_{uuid.uuid4().hex}"
        await self.database.execute(
            security_events.insert().values(
                id=event_id,
                user_id=user_id,
                message=message,
                created_at=datetime.utcnow(),
            )
        )
        return event_id

    async def list_security_events(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        rows = await self.database.fetch_all(
            security_events.select()
            .where(security_events.c.user_id == user_id)
            .order_by(security_events.c.created_at.desc())
            .limit(limit)
        )
        return [dict(r) for r in rows]

    async def add_ip_whitelist(self, user_id: str, ip: str):
        await self.database.execute(
            ip_whitelist.insert().values(
                id=f"ip_{uuid.uuid4().hex}",
                user_id=user_id,
                ip=ip,
                created_at=datetime.utcnow(),
            )
        )

    async def list_ip_whitelist(self, user_id: str) -> List[str]:
        rows = await self.database.fetch_all(ip_whitelist.select().where(ip_whitelist.c.user_id == user_id))
        return [r["ip"] for r in rows]

    async def create_security_action(self, user_id: str, action: str) -> str:
        action_id = f"seca_{uuid.uuid4().hex}"
        await self.database.execute(
            security_actions.insert().values(
                id=action_id,
                user_id=user_id,
                action=action,
                status="requested",
                created_at=datetime.utcnow(),
            )
        )
        return action_id



    # ---------------- Agreements ----------------
    async def record_agreement(self, user_id: str, agreement_version: str, ip_address: str | None, user_agent: str | None) -> str:
        agreement_id = f"agr_{uuid.uuid4().hex}"
        await self.database.execute(
            user_agreements.insert().values(
                id=agreement_id,
                user_id=user_id,
                agreement_version=agreement_version,
                accepted_at=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        return agreement_id

    async def get_latest_agreement(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = await self.database.fetch_one(
            user_agreements.select()
            .where(user_agreements.c.user_id == user_id)
            .order_by(user_agreements.c.accepted_at.desc())
        )
        return dict(row) if row else None

    # ---------------- Onboarding Payments ----------------
        payment_id = f"onb_{uuid.uuid4().hex}"
        await self.database.execute(
            onboarding_payments.insert().values(
                id=payment_id,
                user_id=user_id,
                amount_cents=amount_cents,
                currency=currency,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        return payment_id

        await self.database.execute(
            onboarding_payments.update()
            .values(status=status, updated_at=datetime.utcnow())
        )

    async def get_onboarding_payment(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = await self.database.fetch_one(
            onboarding_payments.select()
            .where(onboarding_payments.c.user_id == user_id)
            .order_by(onboarding_payments.c.created_at.desc())
        )
        return dict(row) if row else None

        row = await self.database.fetch_one(
        )
        return dict(row) if row else None

    # ---------------- Proofs ----------------
    async def create_proof(self, proof: Dict[str, Any]) -> str:
        proof_id = proof.get("id") or f"prf_{uuid.uuid4().hex}"
        data = {
            "id": proof_id,
            "user_id": proof.get("user_id"),
            "job_id": proof.get("job_id"),
            "workflow_id": proof.get("workflow_id"),
            "step_id": proof.get("step_id"),
            "file_path": proof.get("file_path"),
            "owner_agent": proof.get("owner_agent"),
            "proof_type": proof.get("proof_type", "workflow"),
            "status": proof.get("status", "completed"),
            "details": proof.get("details"),
            "artifacts": proof.get("artifacts"),
            "created_at": proof.get("created_at") or datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.database.execute(proofs.insert().values(**data))
        return proof_id

    async def list_proofs(self, user_id: Optional[str] = None, job_id: Optional[str] = None, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = proofs.select()
        if user_id:
            query = query.where(proofs.c.user_id == user_id)
        if job_id:
            query = query.where(proofs.c.job_id == job_id)
        if workflow_id:
            query = query.where(proofs.c.workflow_id == workflow_id)
        rows = await self.database.fetch_all(query.order_by(proofs.c.created_at.desc()))
        return [dict(r) for r in rows]


# Singleton instance
db = DatabaseManager()
