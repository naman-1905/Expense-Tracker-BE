import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Transaction, User

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET must be configured")
ALGORITHM = "HS256"
passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

app = FastAPI(title="Expense Tracker API", description="Single FastAPI service for auth, transactions, and history", version="2.0.0")
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,capacitor://localhost,http://localhost").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class Signup(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str


class TransactionInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    amount: int = Field(gt=0)
    type: str
    emoji: Optional[str] = None
    date: Optional[datetime] = None


class TransactionPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[int] = Field(default=None, gt=0)
    type: Optional[str] = None
    emoji: Optional[str] = None


def token_for(user: User, expires: timedelta = timedelta(hours=24)) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user.email, "userId": user.user_id, "email": user.email, "iat": now, "exp": now + expires}, SECRET_KEY, algorithm=ALGORITHM)


def user_payload(user: User):
    return {"id": user.user_id, "user_id": user.user_id, "name": user.name, "email": user.email, "createdOn": user.created_on}


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub") or payload.get("email")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    user = db.query(User).filter(User.email == email).first() if email else None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def transaction_payload(row: Transaction):
    return {"transaction_id": row.transaction_id, "name": row.name, "title": row.name, "amount": row.amount, "date": row.date, "type": row.type, "emoji": row.emoji, "user_id": row.user_id}


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Expense Tracker API is running", "service": "fastapi", "version": "2.0.0"}


@app.get("/health")
@app.get("/api/history/health")
def health():
    return {"status": "healthy", "service": "fastapi", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/users/signup", status_code=201)
@app.post("/api/auth/signup", status_code=201)
def signup(payload: Signup, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="User already exists with this email")
    user = User(name=payload.name.strip(), email=email, password=passwords.hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = token_for(user)
    return {"message": "User created successfully", "user": user_payload(user), "token": token, "access_token": token, "refreshToken": token_for(user, timedelta(days=7))}


@app.post("/api/users/login")
@app.post("/api/auth/login")
def login(payload: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not passwords.verify(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = token_for(user)
    return {"message": "Login successful", "user": user_payload(user), "token": token, "access_token": token, "refreshToken": token_for(user, timedelta(days=7))}


@app.post("/api/auth/refresh")
def refresh(payload: dict, db: Session = Depends(get_db)):
    value = payload.get("refreshToken") or payload.get("refresh_token")
    try:
        claims = jwt.decode(value, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.email == (claims.get("sub") or claims.get("email"))).first()
    except (JWTError, TypeError):
        user = None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {"token": token_for(user), "access_token": token_for(user)}


@app.get("/api/users/profile")
@app.get("/api/auth/profile")
def profile(user: User = Depends(current_user)):
    return {"user": user_payload(user)}


@app.put("/api/users/me")
def update_profile(payload: Signup, user: User = Depends(current_user), db: Session = Depends(get_db)):
    email = payload.email.lower()
    if email != user.email and db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user.name, user.email, user.password = payload.name.strip(), email, passwords.hash(payload.password)
    db.commit()
    db.refresh(user)
    return user_payload(user)


@app.delete("/api/users/me", status_code=204)
def delete_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()


@app.post("/api/transactions/create", status_code=201)
def create_transaction(payload: TransactionInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    kind = payload.type.lower()
    if kind not in {"income", "expense", "savings"}:
        raise HTTPException(status_code=400, detail="Transaction type must be income, expense, or savings")
    row = Transaction(name=payload.name.strip(), amount=payload.amount, type=kind, emoji=payload.emoji, date=payload.date or datetime.now(timezone.utc), user_id=user.user_id)
    db.add(row); db.commit(); db.refresh(row)
    return transaction_payload(row)


@app.get("/api/transactions/list")
def list_transactions(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), transaction_type: Optional[str] = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = db.query(Transaction).filter(Transaction.user_id == user.user_id)
    if transaction_type:
        kind = transaction_type.lower()
        if kind not in {"income", "expense", "savings"}:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
        query = query.filter(Transaction.type == kind)
    return [transaction_payload(row) for row in query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()]


def owned_transaction(transaction_id: int, user: User, db: Session):
    row = db.query(Transaction).filter(Transaction.transaction_id == transaction_id, Transaction.user_id == user.user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return row


@app.get("/api/transactions/get/{transaction_id}")
def get_transaction(transaction_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return transaction_payload(owned_transaction(transaction_id, user, db))


@app.put("/api/transactions/update/{transaction_id}")
def update_transaction(transaction_id: int, payload: TransactionPatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = owned_transaction(transaction_id, user, db)
    changes = payload.model_dump(exclude_unset=True)
    if "type" in changes:
        changes["type"] = changes["type"].lower()
        if changes["type"] not in {"income", "expense", "savings"}:
            raise HTTPException(status_code=400, detail="Invalid transaction type")
    for key, value in changes.items():
        setattr(row, key, value)
    db.commit(); db.refresh(row)
    return transaction_payload(row)


@app.delete("/api/transactions/delete/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(owned_transaction(transaction_id, user, db)); db.commit()


def user_transactions(user: User, db: Session):
    return db.query(Transaction).filter(Transaction.user_id == user.user_id)


@app.get("/api/transactions/summary/monthly")
def monthly_summary(year: int, month: int = Query(ge=1, le=12), user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = user_transactions(user, db).filter(extract("year", Transaction.date) == year, extract("month", Transaction.date) == month).all()
    income = sum(row.amount for row in rows if row.type == "income")
    expense = sum(row.amount for row in rows if row.type == "expense")
    return {"year": year, "month": month, "total_income": income, "total_expenses": expense, "net_amount": income-expense, "transaction_count": len(rows), "income_count": sum(row.type == "income" for row in rows), "expense_count": sum(row.type == "expense" for row in rows)}


@app.get("/api/history/balance")
def balance(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = user_transactions(user, db).all()
    income = sum(row.amount for row in rows if row.type == "income")
    expenses = sum(row.amount for row in rows if row.type == "expense")
    return {"balance": income-expenses, "total_income": income, "total_expenses": expenses}


@app.get("/api/history/income")
def total_income(user: User = Depends(current_user), db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.type == "income").scalar()
    return {"total_income": int(total)}


@app.get("/api/history/expenses")
def total_expenses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.user_id == user.user_id, Transaction.type == "expense").scalar()
    return {"total_expenses": int(total)}


@app.get("/api/history/transactions")
def history_transactions(days: int = Query(30, ge=1, le=3650), limit: int = Query(100, ge=1, le=500), start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = user_transactions(user, db)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if not start_date and not end_date:
        query = query.filter(Transaction.date >= datetime.now(timezone.utc) - timedelta(days=days))
    rows = query.order_by(Transaction.date.desc()).limit(limit).all()
    return {"transactions": [transaction_payload(row) for row in rows], "count": len(rows), "days": days, "limit": limit}
