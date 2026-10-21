from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="Office Loan Policy Assistant",
    description="AI-powered assistant for office loan policy guidance",
    version="1.0.0",
)


# Define the application's root endpoint
@app.get("/")
def home() -> dict[str,str]:
    return{"message":"Welcome to the Office Loan Policy Assistant"}