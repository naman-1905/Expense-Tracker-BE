#!/usr/bin/env python3
"""
Debug FastAPI user lookup in expense schema
Run from fastapi-crud directory: python3 debug_fastapi_user.py
"""

import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User
from sqlalchemy import text

def debug_fastapi_user():
    print("🔍 FastAPI User Debug")
    print("=" * 30)
    
    db = SessionLocal()
    try:
        # Check current search path
        search_path = db.execute(text("SHOW search_path")).scalar()
        print(f"Current search_path: {search_path}")
        
        # Try to find user using FastAPI's method
        user = db.query(User).filter(User.email == "namanoj19@gmail.com").first()
        if user:
            print(f"✅ User found via FastAPI models:")
            print(f"   ID: {user.user_id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
        else:
            print("❌ User NOT found via FastAPI models")
            
            # Check if user exists in expense schema directly
            result = db.execute(text(
                "SELECT user_id, name, email FROM expense.users WHERE email = 'namanoj19@gmail.com'"
            )).fetchone()
            
            if result:
                print(f"✅ User exists in expense.users directly:")
                print(f"   ID: {result[0]}, Name: {result[1]}, Email: {result[2]}")
                print("❌ But FastAPI models can't see it - schema configuration issue")
            else:
                print("❌ User doesn't exist in expense.users either")
        
        # List all users FastAPI can see
        all_users = db.query(User).all()
        print(f"\nUsers visible to FastAPI: {len(all_users)}")
        for u in all_users:
            print(f"   - {u.email} (ID: {u.user_id})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_fastapi_user()