"""
MongoDB Configuration and Management
Provides proper MongoDB integration with connection pooling, validation, and error handling
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncClient, AsyncDatabase, AsyncCollection
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger(__name__)


class MongoConfig:
    """MongoDB configuration settings."""

    # Connection string from environment
    MONGO_URL = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"
    )

    # Database name
    DB_NAME = os.getenv("MONGODB_DB_NAME", "optik")

    # Connection pool settings
    MAX_POOL_SIZE = int(os.getenv("MONGODB_MAX_POOL_SIZE", "50"))
    MIN_POOL_SIZE = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))

    # Timeout settings
    CONNECT_TIMEOUT_MS = int(os.getenv("MONGODB_CONNECT_TIMEOUT", "5000"))
    SOCKET_TIMEOUT_MS = int(os.getenv("MONGODB_SOCKET_TIMEOUT", "5000"))

    # Replica set (optional)
    REPLICA_SET = os.getenv("MONGODB_REPLICA_SET", None)

    # Authentication (if needed)
    MONGO_USER = os.getenv("MONGODB_USER", None)
    MONGO_PASSWORD = os.getenv("MONGODB_PASSWORD", None)

    @classmethod
    def get_connection_string(cls) -> str:
        """Build MongoDB connection string with all settings."""
        url = cls.MONGO_URL

        # Add authentication if provided
        if cls.MONGO_USER and cls.MONGO_PASSWORD:
            # Handle special characters in password
            password = cls.MONGO_PASSWORD.replace("@", "%40").replace(":", "%3A")
            url = url.replace("mongodb://", f"mongodb://{cls.MONGO_USER}:{password}@")

        # Add connection options
        options = {
            "maxPoolSize": cls.MAX_POOL_SIZE,
            "minPoolSize": cls.MIN_POOL_SIZE,
            "connectTimeoutMS": cls.CONNECT_TIMEOUT_MS,
            "socketTimeoutMS": cls.SOCKET_TIMEOUT_MS,
            "serverSelectionTimeoutMS": cls.CONNECT_TIMEOUT_MS,
            "retryWrites": True,
            "w": "majority",  # Write concern
        }

        if cls.REPLICA_SET:
            options["replicaSet"] = cls.REPLICA_SET

        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in options.items()])
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}{query_string}"


class MongoDBManager:
    """
    Manages MongoDB connections and operations.
    Provides async/await interface with connection pooling.
    """

    def __init__(self):
        """Initialize MongoDB manager."""
        self.client: Optional[AsyncClient] = None
        self.db: Optional[AsyncDatabase] = None
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Establish MongoDB connection with proper error handling.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            connection_string = MongoConfig.get_connection_string()
            logger.info("Connecting to MongoDB...")

            # Create async client
            self.client = AsyncClient(
                connection_string,
                maxPoolSize=MongoConfig.MAX_POOL_SIZE,
                minPoolSize=MongoConfig.MIN_POOL_SIZE,
                connectTimeoutMS=MongoConfig.CONNECT_TIMEOUT_MS,
                socketTimeoutMS=MongoConfig.SOCKET_TIMEOUT_MS,
                serverSelectionTimeoutMS=MongoConfig.CONNECT_TIMEOUT_MS,
            )

            # Test connection
            await self.client.admin.command('ping')

            # Get database
            self.db = self.client[MongoConfig.DB_NAME]
            self.is_connected = True

            logger.info(f"✅ Connected to MongoDB database: {MongoConfig.DB_NAME}")

            # Create indexes
            await self._create_indexes()

            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self):
        """Create database indexes for performance."""
        try:
            # Jobs collection indexes
            jobs = self.db["jobs"]
            await jobs.create_index("user_id")
            await jobs.create_index("status")
            await jobs.create_index("created_at")
            await jobs.create_index([("user_id", 1), ("status", 1)])

            # Products collection indexes
            products = self.db["products"]
            await products.create_index("user_id")
            await products.create_index("name")
            await products.create_index("status")
            await products.create_index("created_at")

            # Conversions collection indexes
            conversions = self.db["conversions"]
            await conversions.create_index("job_id")
            await conversions.create_index("created_at")

            # Deployments collection indexes
            deployments = self.db["deployments"]
            await deployments.create_index("job_id")
            await deployments.create_index("tx_hash")
            await deployments.create_index("merchant_pda")

            # Integrations collection indexes
            integrations = self.db["integrations"]
            await integrations.create_index("user_id")
            await integrations.create_index("name")
            await integrations.create_index("status")

            logger.info("✅ Database indexes created")

        except Exception as e:
            logger.error(f"⚠️ Error creating indexes: {str(e)}")

    def get_collection(self, collection_name: str) -> AsyncCollection:
        """Get reference to a collection."""
        if not self.is_connected or not self.db:
            raise RuntimeError("MongoDB not connected")
        return self.db[collection_name]

    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB health and connection status."""
        try:
            if not self.is_connected or not self.client:
                return {
                    "status": "disconnected",
                    "message": "MongoDB client not initialized"
                }

            # Ping server
            await self.client.admin.command('ping')

            # Get server info
            server_info = await self.client.server_info()

            # Get database stats
            db_stats = await self.db.command('dbStats')

            return {
                "status": "healthy",
                "database": MongoConfig.DB_NAME,
                "version": server_info.get("version", "unknown"),
                "collections": db_stats.get("collections", 0),
                "data_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
                "storage_size_mb": round(db_stats.get("storageSize", 0) / (1024 * 1024), 2),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global MongoDB manager instance
mongodb: MongoDBManager = MongoDBManager()


# ============================================
# Pydantic Models for MongoDB Documents
# ============================================

class JobDocument(BaseModel):
    """Job document schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    store_url: str
    platform: str  # 'shopify', 'woocommerce', 'custom'
    tier: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    message: str = ""
    error: Optional[str] = None
    deployment_config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProductDocument(BaseModel):
    """Product document schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    supply: str
    sold: int = 0
    price: str
    status: str  # 'Live', 'Draft', 'Sold Out'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversionDocument(BaseModel):
    """Conversion document schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    web3_store_data: Dict[str, Any]
    nft_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeploymentDocument(BaseModel):
    """Deployment document schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    tx_hash: str
    merchant_pda: str
    network: str  # 'devnet', 'testnet', 'mainnet'
    dapp_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IntegrationDocument(BaseModel):
    """Integration document schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    detail: str
    status: str  # 'active', 'inactive', 'pending'
    icon: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Repository Pattern for MongoDB Operations
# ============================================

class BaseRepository:
    """Base repository for MongoDB operations."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def get_collection(self) -> AsyncCollection:
        """Get collection reference."""
        return mongodb.get_collection(self.collection_name)

    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document."""
        collection = self.get_collection()
        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def read(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Read single document."""
        collection = self.get_collection()
        return await collection.find_one(query)

    async def read_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Read document by ID."""
        collection = self.get_collection()
        return await collection.find_one({"id": doc_id})

    async def read_all(self, query: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Read multiple documents with pagination."""
        collection = self.get_collection()
        query = query or {}
        cursor = collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def update(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update documents matching query."""
        collection = self.get_collection()
        # Add updated_at timestamp
        update["$set"] = {**update.get("$set", {}), "updated_at": datetime.utcnow()}
        result = await collection.update_many(query, update)
        return result.modified_count

    async def update_by_id(self, doc_id: str, update: Dict[str, Any]) -> bool:
        """Update document by ID."""
        collection = self.get_collection()
        update_data = {"$set": {**update, "updated_at": datetime.utcnow()}}
        result = await collection.update_one({"id": doc_id}, update_data)
        return result.modified_count > 0

    async def delete(self, query: Dict[str, Any]) -> int:
        """Delete documents matching query."""
        collection = self.get_collection()
        result = await collection.delete_many(query)
        return result.deleted_count

    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete document by ID."""
        collection = self.get_collection()
        result = await collection.delete_one({"id": doc_id})
        return result.deleted_count > 0

    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching query."""
        collection = self.get_collection()
        query = query or {}
        return await collection.count_documents(query)

    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists."""
        collection = self.get_collection()
        return await collection.find_one(query) is not None


class JobRepository(BaseRepository):
    """Repository for Jobs collection."""

    def __init__(self):
        super().__init__("jobs")

    async def find_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find jobs by user ID."""
        return await self.read_all({"user_id": user_id}, skip, limit)

    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find jobs by status."""
        return await self.read_all({"status": status}, skip, limit)

    async def find_failed_jobs(self) -> List[Dict[str, Any]]:
        """Find all failed jobs."""
        return await self.read_all({"status": "failed"})


class ProductRepository(BaseRepository):
    """Repository for Products collection."""

    def __init__(self):
        super().__init__("products")

    async def find_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find products by user ID."""
        return await self.read_all({"user_id": user_id}, skip, limit)

    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find products by status."""
        return await self.read_all({"status": status})

    async def search_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search products by name."""
        return await self.read_all({"name": {"$regex": name, "$options": "i"}})


class ConversionRepository(BaseRepository):
    """Repository for Conversions collection."""

    def __init__(self):
        super().__init__("conversions")

    async def find_by_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find conversion by job ID."""
        return await self.read({"job_id": job_id})


class DeploymentRepository(BaseRepository):
    """Repository for Deployments collection."""

    def __init__(self):
        super().__init__("deployments")

    async def find_by_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Find deployment by job ID."""
        return await self.read({"job_id": job_id})

    async def find_by_network(self, network: str) -> List[Dict[str, Any]]:
        """Find deployments by network."""
        return await self.read_all({"network": network})


class IntegrationRepository(BaseRepository):
    """Repository for Integrations collection."""

    def __init__(self):
        super().__init__("integrations")

    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find integrations by user ID."""
        return await self.read_all({"user_id": user_id})

    async def find_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Find integrations by status."""
        return await self.read_all({"status": status})
