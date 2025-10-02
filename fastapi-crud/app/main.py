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

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://expenses.halfskirmish.com",
    "https://crudexpenses.halfskirmish.com",
]

# CORS middleware - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
# Include routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])

@app.get("/")
async def root():
    return {"message": "Expense Tracker API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT_FASTAPI", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)