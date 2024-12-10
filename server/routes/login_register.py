import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt  
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import database.db_helper as db_helper
from dotenv import load_dotenv
from routes.auth import create_access_token, verify_token, get_current_user, hash_password, verify_password

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(request: RegisterRequest):
    if db_helper.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(request.password)

    db_helper.register_user(
        username=request.username,
        email=request.email,
        password=hashed_password,  
        role_id=2,
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number
    )

    return {"message": "User created successfully."}

@router.post("/login")
def login(request: LoginRequest):
    user = db_helper.get_user_by_email(request.email)
    if not user or not verify_password(request.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": request.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']}, you are authorized!"}


@router.get("/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    users = db_helper.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return {"users": users}


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logged out successfully."}
