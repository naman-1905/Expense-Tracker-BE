from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import (
    User, 
    Transaction, 
    TransactionCreate, 
    TransactionResponse, 
    TransactionUpdate
)
from app.auth import get_current_user
from app.utils import validate_transaction_type

router = APIRouter()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Validate transaction type
    if not validate_transaction_type(transaction.type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be 'income' or 'expense'"
        )
    
    # Create transaction
    db_transaction = Transaction(
        name=transaction.name,
        amount=transaction.amount,
        type=transaction.type.lower(),
        emoji=transaction.emoji,
        user_id=current_user.user_id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/", response_model=List[TransactionResponse])
def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of transactions to return"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type (income/expense)")
):
    """Get user's transactions with pagination and filtering"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.user_id)
    
    # Filter by transaction type if provided
    if transaction_type:
        if not validate_transaction_type(transaction_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction type must be 'income' or 'expense'"
            )
        query = query.filter(Transaction.type == transaction_type.lower())
    
    # Order by date descending and apply pagination
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific transaction"""
    # Find the transaction
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update fields if provided
    if transaction_update.name is not None:
        transaction.name = transaction_update.name
    
    if transaction_update.amount is not None:
        transaction.amount = transaction_update.amount
    
    if transaction_update.type is not None:
        if not validate_transaction_type(transaction_update.type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction type must be 'income' or 'expense'"
            )
        transaction.type = transaction_update.type.lower()
    
    if transaction_update.emoji is not None:
        transaction.emoji = transaction_update.emoji
    
    db.commit()
    db.refresh(transaction)
    
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == current_user.user_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return None

@router.get("/summary/monthly")
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    year: int = Query(..., description="Year for the summary"),
    month: int = Query(..., ge=1, le=12, description="Month for the summary")
):
    """Get monthly transaction summary"""
    from sqlalchemy import extract, func
    
    # Get transactions for the specified month and year
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.user_id,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    ).all()
    
    # Calculate summary
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    net_amount = total_income - total_expenses
    
    # Group by type for detailed breakdown
    income_transactions = [t for t in transactions if t.type == 'income']
    expense_transactions = [t for t in transactions if t.type == 'expense']
    
    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": net_amount,
        "transaction_count": len(transactions),
        "income_count": len(income_transactions),
        "expense_count": len(expense_transactions)
    }