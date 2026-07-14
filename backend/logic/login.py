from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
load_dotenv()

def login_portal(req):
    portal_url = os.getenv("PORTAL_LOGIN_URL")
    top_url = os.getenv("PORTAL_TOP_URL")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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
            browser.close()
            return True
        browser.close()
        return False