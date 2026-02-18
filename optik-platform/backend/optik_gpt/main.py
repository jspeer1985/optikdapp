"""
Optik GPT FastAPI Application
Run with: uvicorn optik_gpt.main:app --reload
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .api import router as optik_gpt_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables
REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing_vars:
    logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    logger.warning("Optik GPT will not function without these variables")

# Create FastAPI app
app = FastAPI(
    title="Optik GPT",
    description="The Smartest DApp Creation Assistant - Powered by Anthropic Claude",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(optik_gpt_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if logger.level == logging.DEBUG else "An error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Optik GPT is starting up...")
    logger.info("Optik GPT - The Smartest DApp Creation Assistant")
    logger.info("Powered by Anthropic's Claude")
    logger.info(f"API Docs: http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Optik GPT is shutting down...")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "optik_gpt.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    )
