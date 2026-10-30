import logging
import os
import time
import uuid

from azure.monitor.opentelemetry import configure_azure_monitor

from fastapi import Request
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from office_loan_policy_assistant.api.policy import router as policy_router
from office_loan_policy_assistant.api.auth import router as auth_router
from office_loan_policy_assistant.api.employees import router as employee_router
from office_loan_policy_assistant.api.loans import router as loan_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from office_loan_policy_assistant.core.rate_limit import limiter

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Office Loan Policy Assistant",
    description="AI-powered assistant for office loan policy guidance",
    version="1.0.0",
)

# Initialize Azure Monitor when an Application Insights connection string is available.
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(logger_name="uvicorn.error")

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://office-loan-frontend.grayplant-1453df5e.eastus.azurecontainerapps.io",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        latency_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "API request | request_id=%s | method=%s | "
            "path=%s | status=%s | latency_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            status_code,
            latency_ms,
        )

    response.headers["X-Request-ID"] = request_id

    return response

@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.error(
        "Unhandled API exception | path=%s | error_type=%s",
        request.url.path,
        type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        },
    )

# Register application routers
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(loan_router)
app.include_router(policy_router)


@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Welcome to the Office Loan Policy Assistant"
    }