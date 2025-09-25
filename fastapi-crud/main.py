from fastapi import FastAPI
from routers import transaction

app = FastAPI(title="Transaction CRUD API")

app.include_router(transaction.router, prefix="/transactions", tags=["Transactions"])
