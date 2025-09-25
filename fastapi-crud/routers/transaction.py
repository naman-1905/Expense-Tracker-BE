from fastapi import APIRouter
from db import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class Transaction(BaseModel):
    name: str
    amount: int
    type: str   # "income" or "expense"
    emoji: Optional[str] = None
    user_id: int

@router.post("/")
def create_transaction(tx: Transaction):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (name, amount, type, emoji, user_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING transaction_id
    """, (tx.name, tx.amount, tx.type, tx.emoji, tx.user_id))
    conn.commit()
    return {"transaction_id": cur.fetchone()[0]}

@router.get("/{id}")
def get_transaction(id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE transaction_id=%s", (id,))
    return cur.fetchone()

@router.put("/{id}")
def update_transaction(id: int, tx: Transaction):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE transactions
        SET name=%s, amount=%s, type=%s, emoji=%s, user_id=%s
        WHERE transaction_id=%s
    """, (tx.name, tx.amount, tx.type, tx.emoji, tx.user_id, id))
    conn.commit()
    return {"message": "Transaction updated"}

@router.delete("/{id}")
def delete_transaction(id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE transaction_id=%s", (id,))
    conn.commit()
    return {"message": "Transaction deleted"}
