"""
FastAPI main application.
Health Insurance Denial Prevention & Appeal Assistant Backend.
"""
import sys
import types

# --- MONKEY PATCH FOR PADDLEX/LANGCHAIN COMPATIBILITY ---
# Paddlex expects 'langchain.docstore.document.Document' which was moved in newer LangChain versions.
# We inject a mock module to redirect it to the correct location in 'langchain_core'.
try:
    import langchain.docstore.document
except ImportError:
    try:
        import langchain_core.documents

        # Create mock modules
        docstore = types.ModuleType("langchain.docstore")
        document = types.ModuleType("langchain.docstore.document")

        # Map the Document class
        document.Document = langchain_core.documents.Document
        docstore.document = document

        # Register in sys.modules so imports work
        sys.modules["langchain.docstore"] = docstore
        sys.modules["langchain.docstore.document"] = document

        print("✅ Applied patch for langchain.docstore compatibility")
    except ImportError:
        print("⚠️ Failed to apply langchain.docstore patch")

try:
    import langchain.text_splitter
except ImportError:
    try:
        import langchain_text_splitters

        # Create mock module
        text_splitter = types.ModuleType("langchain.text_splitter")

        # Map the RecursiveCharacterTextSplitter class
        text_splitter.RecursiveCharacterTextSplitter = langchain_text_splitters.RecursiveCharacterTextSplitter

        # Register in sys.modules
        sys.modules["langchain.text_splitter"] = text_splitter

        print("✅ Applied patch for langchain.text_splitter compatibility")
    except ImportError:
        print("⚠️ Failed to apply langchain.text_splitter patch")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from database import init_db
from routes import upload, analyze, appeal, insurance, simulation
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Health Insurance Denial Assistant API",
    description="AI-powered health insurance denial prevention and appeal assistant",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    logger.info(f"Upload folder: {settings.UPLOAD_FOLDER}")
    logger.info(f"Insurance rules directory: {settings.INSURANCE_RULES_DIR}")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "message": "Health Insurance Denial Assistant API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "groq_api_configured": bool(settings.GROQ_API_KEY),
        "upload_folder": str(settings.UPLOAD_FOLDER),
        "models": {
            "extractor": settings.EXTRACTOR_MODEL,
            "reasoning": settings.REASONING_MODEL
        }
    }

# Register routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(appeal.router, prefix="/api", tags=["Appeal"])
app.include_router(insurance.router, prefix="/api", tags=["Insurance"])
app.include_router(simulation.router, prefix="/api", tags=["Simulation"])

from routes import session
app.include_router(session.router, prefix="/api", tags=["Session"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )