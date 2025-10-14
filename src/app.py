import uvicorn, os
from config import get_settings
from fastapi import FastAPI, Request
from routers import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from azure.monitor.opentelemetry import configure_azure_monitor
from contextlib import asynccontextmanager

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    if not getattr(app.state, "otel_configured", False):
        configure_azure_monitor()
        app.state.otel_configured = True
    yield

app = FastAPI(lifespan=lifespan)

# Web app endpoints
app.include_router(api_router.router)

if settings.cors_allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

#tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error :/"},
    )

@app.get("/")
async def home(request: Request):
    return {"status": "healthy", "message": "SMILE Chatbot API up and running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
    
if __name__ == "__main__":
    port = int(os.getenv("PORT", 3978))
    uvicorn.run(
        "src.app:app", 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        reload=False  # Disable reload in production
    )

# $ uvicorn app:app --app-dir src