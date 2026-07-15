# backend/logic/register.py
import json
import os

FILE_PATH = "data/login/login.json"


def save(req, member_no: str):
    os.makedirs("data/login", exist_ok=True)

    data = []

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, encoding="utf-8") as f:
            data = json.load(f)

    new_login = {
        "basic_username": req.basic_username,
        "basic_password": req.basic_password,
        "portal_username": req.portal_username,
        "portal_password": req.portal_password,
        "member_no": member_no,
    }

    if new_login not in data:
        data.append(new_login)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
