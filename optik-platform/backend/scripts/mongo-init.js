/**
 * MongoDB Initialization Script
 * Runs on container startup to set up users and collections
 */

const env = (typeof process !== "undefined" && process.env) ? process.env : {};
const environment = (env.ENVIRONMENT || "production").toLowerCase();
const allowDemo = env.OPTIK_ALLOW_DEMO_DATA === "true" && environment !== "production";

const appUser = env.OPTIK_MONGO_APP_USER || (allowDemo ? "optik_user" : null);
const appPassword = env.OPTIK_MONGO_APP_PASSWORD || (allowDemo ? "optik_password_change_me" : null);

if (!appUser || !appPassword) {
  throw new Error("OPTIK_MONGO_APP_USER and OPTIK_MONGO_APP_PASSWORD are required to initialize MongoDB.");
}

// Switch to admin database
db = db.getSiblingDB('admin');

// Create Optik application user (if not already exists)
try {
  db.createUser({
    user: appUser,
    pwd: appPassword,
    roles: [
      { role: "readWrite", db: "optik" },
      { role: "dbOwner", db: "optik" }
    ]
  });
  print("✅ Created optik_user");
} catch (e) {
  print("⚠️ User might already exist: " + e);
}

// Switch to optik database
db = db.getSiblingDB('optik');

// Create collections with schema validation
print("📚 Creating collections...");

// Jobs Collection
db.createCollection("jobs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "user_id", "store_url", "platform", "status"],
      properties: {
        id: { bsonType: "string", description: "Unique job identifier" },
        user_id: { bsonType: "string", description: "User ID" },
        store_url: { bsonType: "string", description: "Store URL" },
        platform: {
          enum: ["shopify", "woocommerce", "custom"],
          description: "E-commerce platform"
        },
        tier: {
          enum: ["basic", "growth", "global", "scale", "elite"],
          description: "Service tier"
        },
        status: {
          enum: ["pending", "processing", "completed", "failed"],
          description: "Job status"
        },
        message: { bsonType: "string" },
        error: { bsonType: ["string", "null"] },
        deployment_config: { bsonType: ["object", "null"] },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});
print("✅ Created 'jobs' collection");

// Products Collection
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "user_id", "name", "price"],
      properties: {
        id: { bsonType: "string" },
        user_id: { bsonType: "string" },
        name: { bsonType: "string" },
        description: { bsonType: ["string", "null"] },
        supply: { bsonType: "string" },
        sold: { bsonType: "int" },
        price: { bsonType: "string" },
        status: {
          enum: ["Live", "Draft", "Sold Out", "Archived"],
          description: "Product status"
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});
print("✅ Created 'products' collection");

// Conversions Collection
db.createCollection("conversions");
print("✅ Created 'conversions' collection");

// Deployments Collection
db.createCollection("deployments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "job_id", "tx_hash", "network"],
      properties: {
        id: { bsonType: "string" },
        job_id: { bsonType: "string" },
        tx_hash: { bsonType: "string" },
        merchant_pda: { bsonType: "string" },
        network: {
          enum: ["devnet", "testnet", "mainnet"],
          description: "Blockchain network"
        },
        dapp_url: { bsonType: "string" },
        created_at: { bsonType: "date" }
      }
    }
  }
});
print("✅ Created 'deployments' collection");

// Integrations Collection
db.createCollection("integrations");
print("✅ Created 'integrations' collection");

// Create Indexes for Performance
print("📊 Creating indexes...");

// Jobs indexes
db.jobs.createIndex({ user_id: 1 });
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ created_at: -1 });
db.jobs.createIndex({ user_id: 1, status: 1 });
print("✅ Created jobs indexes");

// Products indexes
db.products.createIndex({ user_id: 1 });
db.products.createIndex({ name: "text" });
db.products.createIndex({ status: 1 });
db.products.createIndex({ created_at: -1 });
print("✅ Created products indexes");

// Conversions indexes
db.conversions.createIndex({ job_id: 1 });
db.conversions.createIndex({ created_at: -1 });
print("✅ Created conversions indexes");

// Deployments indexes
db.deployments.createIndex({ job_id: 1 });
db.deployments.createIndex({ tx_hash: 1 });
db.deployments.createIndex({ merchant_pda: 1 });
db.deployments.createIndex({ network: 1 });
print("✅ Created deployments indexes");

// Integrations indexes
db.integrations.createIndex({ user_id: 1 });
db.integrations.createIndex({ name: 1 });
db.integrations.createIndex({ status: 1 });
print("✅ Created integrations indexes");

// Seed initial data (optional)
if (allowDemo) {
  print("📌 Seeding initial data (demo only)...");

  // Sample jobs
  db.jobs.insertMany([
    {
      id: "job_001",
      user_id: "user_demo",
      store_url: "https://demo.shopify.com",
      platform: "shopify",
      tier: "growth",
      status: "completed",
      message: "Store conversion completed",
      deployment_config: {
        network: "devnet",
        treasury: "7dzzihnceMRrhDvDFVH5E4pVKhFeEgLTTfxWczvbHrPa"
      },
      created_at: new Date(),
      updated_at: new Date()
    }
  ]);
  print("✅ Seeded initial data");
} else {
  print("ℹ️ Demo seed data disabled for this environment.");
}

// Setup backup index
db.adminCommand({
  createBackup: 1,
  backupName: "initial_backup"
});

print("\n" + "=".repeat(50));
print("✅ MongoDB initialization complete!");
print("=".repeat(50));
print("\nDatabase: optik");
print("Collections: jobs, products, conversions, deployments, integrations");
print("Indexes: Created for performance optimization");
print("User: optik_user created");
print("\nMongo Express: http://localhost:8081");
print("Admin: admin / admin");
