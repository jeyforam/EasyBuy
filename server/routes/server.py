import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt  
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import database.db_helper as db_helper
from dotenv import load_dotenv


app = FastAPI()

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", 30))

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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token header")

    token = authorization.split("Bearer ")[1]
    payload = verify_token(token)
    user = db_helper.get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Convert the hashed password to bytes if it's stored as a string
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

@app.get("/")
def check():
    return "EasyBuy server is up and running!"

@app.post("/login")
def login(request: LoginRequest):
    user = db_helper.get_user_by_email(request.email)
    if not user or not verify_password(request.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": request.email})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']}, you are authorized!"}

@app.get("/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
    users = db_helper.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return {"users": users}

@app.post("/register")
def register(request: RegisterRequest):
    if db_helper.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing it in the database
    hashed_password = hash_password(request.password)

    db_helper.register_user(
        username=request.username,
        email=request.email,
        password=hashed_password,  # Store the hashed password
        role_id=2,
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number
    )

    return {"message": "User created successfully."}
