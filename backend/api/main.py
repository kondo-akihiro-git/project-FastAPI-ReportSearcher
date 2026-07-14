from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logic.login import login_portal
from model.models import LoginRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(req: LoginRequest):

    success = login_portal(req)

    if success:
        return {
            "message": "login-test"
        }

    return {
        "message": "login-failed"
    }


@app.get("/search")
def search():
    return {
        "message": "search-test"
    }