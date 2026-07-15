# backend/batch/scraper.py
# 2024年1月〜今月までの週報をポータルから取得し、data/report/ にJSONで保存する
import json
import os
import re
import time
from datetime import date
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

LOGIN_FILE = "data/login/login.json"
REPORT_DIR = "data/report"

START_YEAR_MONTH = (2024, 1)   # 固定の下限：2024年1月
PAGE_TIMEOUT_MS = 45000
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 3  # 1回目失敗→3秒待機、2回目失敗→6秒待機...

# ページを軽量化してタイムアウトを起きにくくするため、これらはブロックする
BLOCKED_RESOURCE_TYPES = {"image", "media", "font", "stylesheet"}


# ---------- ユーティリティ ----------

# ログイン情報一覧を読み込む
def load_logins() -> list[dict]:
    with open(LOGIN_FILE, encoding="utf-8") as f:
        return json.load(f)


# 週報一覧ページのURLを組み立てる
def get_weekly_report_url_base() -> str:
    explicit = os.getenv("PORTAL_WEEKLY_REPORT_URL")
    if explicit:
        return explicit
    parsed = urlparse(os.getenv("PORTAL_TOP_URL"))
    return f"{parsed.scheme}://{parsed.netloc}/weekly_report"


# 2024年1月〜今月までの (year, month) を返す
def get_target_year_months() -> list[tuple[int, int]]:
    start_year, start_month = START_YEAR_MONTH
    today = date.today()

    result = []
    year, month = today.year, today.month
    while (year, month) >= (start_year, start_month):
        result.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return result


# 保存先のファイルパスを組み立てる
def report_filepath(username: str, member_no: str, year_month: str, week_num: int) -> str:
    filename = f"{year_month}-{week_num}-{username}-{member_no}.json"
    return os.path.join(REPORT_DIR, filename)


# 週報データをJSONファイルに保存する
def save_report(username: str, member_no: str, report: dict):
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = report_filepath(username, member_no, report["year_month"], report["week_num"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  保存しました: {path}")


# 画像・CSS・フォント・動画などをブロックしてページを軽量化する
def block_heavy_resources(page):
    def handler(route):
        if route.request.resource_type in BLOCKED_RESOURCE_TYPES:
            route.abort()
        else:
            route.continue_()
    page.route("**/*", handler)


# ページ遷移。失敗時は指数バックオフで最大MAX_RETRIES回リトライする
def goto_with_retry(page, url: str, label: str) -> bool:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            return True
        except Exception as e:
            last_error = e
            wait_sec = RETRY_BACKOFF_SEC * attempt
            print(f"  [{label}] 失敗 ({attempt}/{MAX_RETRIES}): {e.__class__.__name__} "
                  f"-> {wait_sec}秒後にリトライ")
            time.sleep(wait_sec)

    print(f"  [{label}] 全リトライ失敗、スキップします: {last_error}")
    return False


# その月に実際に存在する週番号一覧をセレクトボックスから取得する
def get_available_weeks(page) -> list[int]:
    options = page.locator("select[name='weekly_report_week_num'] option")
    weeks = []
    for i in range(options.count()):
        value = options.nth(i).get_attribute("value")
        if value:
            weeks.append(int(value))
    return weeks


# ---------- HTML抽出 ----------

# 『直近で学んだこと』『コメント欄』などのラベルを含むブロックのテキストを抽出する
def extract_section(soup: BeautifulSoup, keyword: str) -> str:
    for div in soup.find_all("div", style=re.compile("margin: 40px auto 40px")):
        if keyword in div.get_text():
            textarea = div.find("textarea")
            if textarea is not None:
                return textarea.get_text().strip()
            readonly = div.find("div", class_="readonly_area")
            if readonly is not None:
                return readonly.get_text("\n").strip()
    return ""


# 月〜日の日報（作業内容）を抽出する。未入力の日はスキップする
def extract_daily_reports(soup: BeautifulSoup) -> list[dict]:
    reports = []
    table = soup.find("table", id="weekly_report_list")
    if table is None or table.find("tbody") is None:
        return reports

    for tr in table.find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        report_date = tds[0].get_text(strip=True)
        content_td = tds[3]

        textarea = content_td.find("textarea")
        if textarea is not None:
            content = textarea.get_text().strip()
        else:
            readonly = content_td.find("div", class_="readonly_area")
            content = readonly.get_text("\n").strip() if readonly else ""

        if not content:
            continue

        reports.append({"date": report_date, "content": content})

    return reports


# リーダー・社長・その他からの返信を抽出する
def extract_replies(soup: BeautifulSoup) -> dict:
    return {
        "leader": extract_section(soup, "リーダーからの返信"),
        "president": extract_section(soup, "社長からの返信"),
        "other": extract_section(soup, "その他の返信"),
    }


# ページ全体から週報データを組み立てる。中身が空の週はNoneを返す
def build_report(soup: BeautifulSoup, member_no: str, year_month: str, week_num: int) -> dict:
    daily_reports = extract_daily_reports(soup)
    studying_memo = extract_section(soup, "直近で学んだこと")
    comment = extract_section(soup, "コメント欄")

    return {
        "year_month": year_month,
        "week_num": week_num,
        "member_no": member_no,
        "daily_reports": daily_reports,
        "studying_memo": studying_memo,
        "comment": comment,
        "replies": extract_replies(soup),
    }


# ---------- スクレイピング本体 ----------

# 1ユーザー分、ログインしてから対象期間の週報を取得する
def scrape_login(p, login: dict, weekly_report_url_base: str):
    username = login["portal_username"]
    member_no = login["member_no"]

    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        http_credentials={
            "username": login["basic_username"],
            "password": login["basic_password"],
        }
    )
    page = context.new_page()
    block_heavy_resources(page)

    portal_url = os.getenv("PORTAL_LOGIN_URL")
    top_url = os.getenv("PORTAL_TOP_URL")

    if not goto_with_retry(page, portal_url, f"{username} ログインページ"):
        print(f"ログインページに到達できませんでした: {username}")
        browser.close()
        return

    page.locator("input[name='login_id']").fill(login["portal_username"])
    page.locator("input[name='login_pass']").fill(login["portal_password"])
    page.locator("button[name='accept']").click()
    page.wait_for_load_state("domcontentloaded")

    if page.url != top_url:
        print(f"ログインに失敗しました: {username}")
        browser.close()
        return

    year_months = [f"{y:04d}-{m:02d}" for y, m in get_target_year_months()]
    print(f"[{username}] 対象月: {', '.join(year_months)} ({len(year_months)}ヶ月)")

    success_count = 0
    skip_count = 0
    fail_count = 0

    for year_month in year_months:
        base_url = (f"{weekly_report_url_base}?member_no={member_no}"
                    f"&weekly_report_year_month={year_month}&weekly_report_week_num=1")

        if not goto_with_retry(page, base_url, f"{year_month} 月一覧"):
            fail_count += 1
            continue

        weeks = get_available_weeks(page)
        if not weeks:
            continue

        for week_num in weeks:
            existing_path = report_filepath(username, member_no, year_month, week_num)
            if os.path.exists(existing_path):
                skip_count += 1
                continue

            url = (f"{weekly_report_url_base}?member_no={member_no}"
                   f"&weekly_report_year_month={year_month}&weekly_report_week_num={week_num}")
            label = f"{year_month} 第{week_num}週"

            if not goto_with_retry(page, url, label):
                fail_count += 1
                continue

            soup = BeautifulSoup(page.content(), "html.parser")
            report = build_report(soup, member_no, year_month, week_num)
            if report:
                save_report(username, member_no, report)
                success_count += 1

    browser.close()
    print(f"[{username}] 完了: 保存 {success_count} / スキップ(既存) {skip_count} / 失敗 {fail_count}")

def check_existing_reports(page, login: dict, weekly_report_url_base: str) -> bool:
    username = login["portal_username"]
    member_no = login["member_no"]

    year_months = [
        f"{y:04d}-{m:02d}"
        for y, m in get_target_year_months()
    ]

    for year_month in year_months:

        base_url = (
            f"{weekly_report_url_base}"
            f"?member_no={member_no}"
            f"&weekly_report_year_month={year_month}"
            f"&weekly_report_week_num=1"
        )

        if not goto_with_retry(
            page,
            base_url,
            f"{year_month}確認"
        ):
            return False

        weeks = get_available_weeks(page)

        for week_num in weeks:

            path = report_filepath(
                username,
                member_no,
                year_month,
                week_num
            )

            if not os.path.exists(path):
                return False

    return True

# 全ログイン情報についてスクレイピングを実行する
def main():
    logins = load_logins()
    weekly_report_url_base = get_weekly_report_url_base()

    with sync_playwright() as p:
        for login in logins:
            scrape_login(p, login, weekly_report_url_base)


if __name__ == "__main__":
    main()