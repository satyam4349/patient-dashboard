"""
FastAPI main application for Agent Companion API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.agent_companion_routes import router as agent_router

# Create FastAPI app
app = FastAPI(
    title="Agent Companion API",
    description="AI-powered mental health companion API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router)

@app.get("/")
async def root():
    return {"message": "Agent Companion API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)