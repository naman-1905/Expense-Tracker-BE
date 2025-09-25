from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    name: str
    amount: int
    type: str               # "income" or "expense"
    emoji: Optional[str] = None
    user_id: int

class TransactionOut(Transaction):
    transaction_id: int
    date: datetime
