# backend/logic/check.py

import json
import os
from datetime import date
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

LOGIN_FILE = "data/login/login.json"
REPORT_DIR = "data/report"
START_YEAR_MONTH = (2024, 1)
PAGE_TIMEOUT_MS = 45000


def load_logins():
    with open(LOGIN_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_weekly_report_url_base():
    explicit = os.getenv("PORTAL_WEEKLY_REPORT_URL")

    if explicit:
        return explicit

    parsed = urlparse(os.getenv("PORTAL_TOP_URL"))
    return f"{parsed.scheme}://{parsed.netloc}/weekly_report"


def get_target_year_months():

    start_year, start_month = START_YEAR_MONTH
    today = date.today()

    result = []

    year = today.year
    month = today.month

    while (year, month) >= (start_year, start_month):
        result.append(
            f"{year:04d}-{month:02d}"
        )

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    return result


def report_filepath(username, member_no, year_month, week_num):

    filename = (
        f"{year_month}-{week_num}-{username}-{member_no}.json"
    )

    return os.path.join(
        REPORT_DIR,
        filename
    )


def goto_page(page, url):

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=PAGE_TIMEOUT_MS
        )
        return True

    except Exception:
        return False


def get_available_weeks(page):

    options = page.locator(
        "select[name='weekly_report_week_num'] option"
    )

    weeks = []

    for i in range(options.count()):
        value = options.nth(i).get_attribute("value")

        if value:
            weeks.append(int(value))

    return weeks

from datetime import date, timedelta


def get_target_reports():
    start_date = date(START_YEAR_MONTH[0], START_YEAR_MONTH[1], 1)
    today = date.today()

    result = []

    current = start_date

    while current <= today:

        # 月曜日まで戻す
        monday = current - timedelta(days=current.weekday())

        year_month = current.strftime("%Y-%m")

        first_monday = date(current.year, current.month, 1)
        first_monday -= timedelta(days=first_monday.weekday())

        week_num = ((monday - first_monday).days // 7) + 1

        result.append(
            (
                year_month,
                week_num
            )
        )

        current += timedelta(days=7)

    return list(dict.fromkeys(result))

def check_reports_for_user(login):

    username = login["portal_username"]
    member_no = login["member_no"]

    for year_month, week_num in get_target_reports():

        path = report_filepath(
            username,
            member_no,
            year_month,
            week_num
        )

        if not os.path.exists(path):
            print(f"不足ファイル: {path}")
            return False

    return True


def check_reports():

    logins = load_logins()

    for login in logins:
        if not check_reports_for_user(login):
            return False

    return True