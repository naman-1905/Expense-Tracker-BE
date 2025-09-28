from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'expense'}
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)
    created_on = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name='check_transaction_type'),
        {'schema': 'expense'}
    )
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, server_default=func.current_timestamp())
    type = Column(String(20), nullable=False)
    emoji = Column(String(10), nullable=True)
    user_id = Column(Integer, ForeignKey("expense.users.user_id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="transactions")

# Pydantic Models for API
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    created_on: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TransactionBase(BaseModel):
    name: str
    amount: int
    type: str
    emoji: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[int] = None
    type: Optional[str] = None
    emoji: Optional[str] = None

class TransactionResponse(TransactionBase):
    transaction_id: int
    date: datetime
    user_id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None