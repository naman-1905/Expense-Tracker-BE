from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, transactions
from app.database import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Tracker API",
    description="A FastAPI backend for expense tracking",
    version="1.0.0"
)

# CRITICAL: Define origins as a list of strings
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://expenses.halfskirmish.com",
    "https://crudexpenses.halfskirmish.com",
    "https://authexpenses.halfskirmish.com",
    "https://historyexpenses.halfskirmish.com",
    "https://financeauth.halfskirmish.com",
    "https://financecrud.halfskirmish.com",
    "https://financehistory.halfskirmish.com",
]

# CORS middleware - MUST be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,
)

# Include routers AFTER middleware
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])

@app.get("/")
async def root():
    return {
        "message": "Expense Tracker API is running!",
        "service": "fastapi-crud",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-crud"
    }

# Remove the generic OPTIONS handler - let CORS middleware handle it

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT_FASTAPI", 5000))
    print(f"Starting FastAPI CRUD service on port {port}")
    print(f"Allowed origins: {origins}")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )