"""
FastAPI Main Application
Excel to CSV conversion tool with multi-sheet support
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Excel to CSV API",
    description="Convert Excel files to CSV with multi-sheet support",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)

# Mount static files for downloads
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)
app.mount("/downloads", StaticFiles(directory=settings.OUTPUT_DIR), name="downloads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Excel to CSV API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
