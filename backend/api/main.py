# backend/api/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from logic.search import search_reports, DEFAULT_PAGE_SIZE
from logic import runner
from logic.register import save
from logic.login import login_check
from model.models import LoginRequest
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
frontend_url = os.getenv("VITE_FRONTEND_URL")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(req: LoginRequest):
    success, member_no = login_check(req)
    if not success:
        raise HTTPException(status_code=401, detail="ポータルへのログインに失敗しました")
    save(req, member_no)
    return {"member_no": member_no}


@app.get("/scrape/check")
def scrape_check():
    from logic.check import check_reports

    return {
        "completed": check_reports()
    }


@app.post("/scrape/start")
def scrape_start():
    started = runner.start_scrape()
    return {"status": "started" if started else "already_running"}


@app.get("/scrape/status")
def scrape_status():
    return runner.get_status()


@app.get("/search")
def search(keyword: str, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE):
    return search_reports(keyword, page=page, page_size=page_size)