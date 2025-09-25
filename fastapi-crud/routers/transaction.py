from fastapi import APIRouter, HTTPException
from db import get_db_cursor
from models import Transaction, TransactionOut
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

@router.post("/", response_model=Dict[str, int])
def create_transaction(tx: Transaction):
    """Create a new transaction"""
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO transactions (name, amount, type, emoji, user_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING transaction_id
            """, (tx.name, tx.amount, tx.type, tx.emoji, tx.user_id))
            transaction_id = cur.fetchone()[0]
            return {"transaction_id": transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")

@router.get("/{id}")
def get_transaction(id: int):
    """Get a transaction by ID"""
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT transaction_id, name, amount, type, emoji, user_id, created_at
                FROM transactions 
                WHERE transaction_id = %s
            """, (id,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            # Convert to dictionary for better response structure
            return {
                "transaction_id": result[0],
                "name": result[1],
                "amount": result[2],
                "type": result[3],
                "emoji": result[4],
                "user_id": result[5],
                "created_at": result[6]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transaction: {str(e)}")

@router.get("/user/{user_id}")
def get_user_transactions(user_id: int):
    """Get all transactions for a specific user"""
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT transaction_id, name, amount, type, emoji, user_id, created_at
                FROM transactions 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            results = cur.fetchall()
            
            transactions = []
            for row in results:
                transactions.append({
                    "transaction_id": row[0],
                    "name": row[1],
                    "amount": row[2],
                    "type": row[3],
                    "emoji": row[4],
                    "user_id": row[5],
                    "created_at": row[6]
                })
            
            return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user transactions: {str(e)}")

@router.put("/{id}")
def update_transaction(id: int, tx: Transaction):
    """Update a transaction"""
    try:
        with get_db_cursor() as cur:
            # First check if transaction exists
            cur.execute("SELECT transaction_id FROM transactions WHERE transaction_id = %s", (id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            # Update the transaction
            cur.execute("""
                UPDATE transactions
                SET name = %s, amount = %s, type = %s, emoji = %s, user_id = %s
                WHERE transaction_id = %s
            """, (tx.name, tx.amount, tx.type, tx.emoji, tx.user_id, id))
            
            return {"message": "Transaction updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")

@router.delete("/{id}")
def delete_transaction(id: int):
    """Delete a transaction"""
    try:
        with get_db_cursor() as cur:
            # First check if transaction exists
            cur.execute("SELECT transaction_id FROM transactions WHERE transaction_id = %s", (id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            # Delete the transaction
            cur.execute("DELETE FROM transactions WHERE transaction_id = %s", (id,))
            
            return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete transaction: {str(e)}")