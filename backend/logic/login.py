# backend/logic/login.py
from playwright.sync_api import sync_playwright
import os
import re
from dotenv import load_dotenv
load_dotenv()

def login_check(req):
    portal_url = os.getenv("PORTAL_LOGIN_URL")
    top_url = os.getenv("PORTAL_TOP_URL")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            http_credentials={
                "username": req.basic_username,
                "password": req.basic_password,
            }
        )

        page = context.new_page()
        page.goto(portal_url)
        page.locator("input[name='login_id']").fill(req.portal_username)
        page.locator("input[name='login_pass']").fill(req.portal_password)
        page.locator("button[name='accept']").click()
        page.wait_for_load_state("networkidle")

        if top_url == page.url:
            member_no = _extract_member_no(page)
            browser.close()
            return True, member_no

        browser.close()
        return False, None


def _extract_member_no(page) -> str | None:
    try:
        text = page.locator(".user-header p").inner_text()
        match = re.search(r"ID[:：]\s*(\d+)", text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None