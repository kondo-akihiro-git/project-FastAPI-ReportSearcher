# backend/logic/check.py
import json
import os
from datetime import date, timedelta
from dotenv import load_dotenv
load_dotenv()

LOGIN_FILE = "data/login/login.json"
REPORT_DIR = "data/report"
START_YEAR_MONTH = (2024, 1)

# ユーザー読み込み
def load_login_users():
    with open(LOGIN_FILE, encoding="utf-8") as f:
        return json.load(f)


# 2024年1月〜今月までの (year, month) を返す
def get_target_duration():
    start_date = date(START_YEAR_MONTH[0], START_YEAR_MONTH[1], 1)
    today = date.today()
    result = []
    current = start_date - timedelta(days=start_date.weekday())
    while current <= today:
        for i in range(7):
            target = current + timedelta(days=i)
            if target < start_date or target > today:
                continue
            year_month = target.strftime("%Y-%m")
            first_day = date(target.year, target.month, 1)
            first_monday = first_day - timedelta(days=first_day.weekday())
            week_num = ((current - first_monday).days // 7) + 1
            result.append((year_month, week_num))
        current += timedelta(days=7)
    return list(dict.fromkeys(result))


# 週報のパス組み立て
def report_filepath(username, member_no, year_month, week_num):
    return os.path.join(REPORT_DIR, f"{year_month}-{week_num}-{username}-{member_no}.json")


# 週報ファイル存在確認
def check_reports_for_user(login):
    username = login["portal_username"]
    member_no = login["member_no"]
    for year_month, week_num in get_target_duration():
        path = report_filepath(username, member_no, year_month, week_num)
        if not os.path.exists(path):
            print(f"不足ファイル: {path}")
            return False
    return True


# 全ユーザーの週報ファイル確認
def check_reports():
    for user in load_login_users():
        if not check_reports_for_user(user):
            return False
    return True