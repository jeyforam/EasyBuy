from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import db_helper

app = FastAPI()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str
    

@app.get("/")
def check():
    return "EasyBuy server is up and running!"

@app.post("/easybuy/register")
def register(request: RegisterRequest):

    if db_helper.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")


    db_helper.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        role_id=2
    )

    return {"message": "User registered successfully."}

@app.post("/easybuy/login")
def login(request:LoginRequest):

    is_logged_in = db_helper.login_user(
                    email=request.email,
                    password=request.password
                 )
    
    if not is_logged_in:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful"}
