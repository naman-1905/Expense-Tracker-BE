from fastapi import FastAPI
from routers import transaction
import os
import uvicorn

app = FastAPI(title="Transaction CRUD API")
app.include_router(transaction.router, prefix="/transactions", tags=["Transactions"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # default 5001
    uvicorn.run(app, host="0.0.0.0", port=port)
