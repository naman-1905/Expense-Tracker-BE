from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import User, Transaction

def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user statistics including total income, expenses, and balance"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "total_transactions": len(transactions)
    }

def validate_transaction_type(transaction_type: str) -> bool:
    """Validate if transaction type is valid"""
    return transaction_type.lower() in ['income', 'expense']