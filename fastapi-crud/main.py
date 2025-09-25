from fastapi import FastAPI
from routers import income, expense

app = FastAPI(title="Expense Tracker CRUD")

app.include_router(income.router, prefix="/income", tags=["Income"])
app.include_router(expense.router, prefix="/expense", tags=["Expense"])
