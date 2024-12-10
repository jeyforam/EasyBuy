from fastapi import FastAPI
from routes import login_register

app = FastAPI()

@app.get("/")
def check():
    return "EasyBuy server is up and running!"

app.include_router(login_register.router)