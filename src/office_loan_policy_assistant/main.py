from fastapi import FastAPI

from office_loan_policy_assistant.api.auth import router as auth_router
from office_loan_policy_assistant.api.employees import router as employee_router
from office_loan_policy_assistant.api.loans import router as loan_router


app = FastAPI(
    title="Office Loan Policy Assistant",
    description="AI-powered assistant for office loan policy guidance",
    version="1.0.0",
)

# Register application routers
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(loan_router)


@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Welcome to the Office Loan Policy Assistant"
    }