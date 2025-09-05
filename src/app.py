import logging, uvicorn, traceback, sys
from config import get_settings
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind,get_tracer_provider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from routers import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from azure.monitor.opentelemetry import configure_azure_monitor

settings = get_settings()

# logger = logging.getLogger("app")
# logger.setLevel(logging.INFO if settings.log_level == "INFO" else logging.DEBUG)
# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
# logger.addHandler(handler)

configure_azure_monitor()  # reads APPLICATIONINSIGHTS_CONNECTION_STRING

# Configure the logging system
# logging.basicConfig(
#     level=logging.INFO,  # Logging level
#     format="%(asctime)s %(levelname)s %(name)s %(message)s",  # Log format
#     handlers=[
#         logging.StreamHandler()  # Output logs to the console (stdout)
#     ]
# )
# logger = logging.getLogger(__name__)

app = FastAPI()
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

tracer = trace.get_tracer(__name__, tracer_provider=get_tracer_provider())

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    #logger.error(f"Unhandled exception: {exc}")
    traceback_str = ''.join(traceback.format_tb(exc.__traceback__))
    #logger.error(f"Traceback: {traceback_str}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error :/"},
    )

@app.get("/")
async def home(request: Request):
    with tracer.start_as_current_span("home_request", context=extract(request.headers), kind=SpanKind.SERVER):
        #logger.info("Home request")
        return "SMILE Chatbot API up and running"
    
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3978, log_level="trace", reload=True)

# $ uvicorn app:app --app-dir src