from playwright.sync_api import sync_playwright


def login_portal(req):

    print("========== ログイン開始 ==========")

    with sync_playwright() as p:

        print("Chromium起動")

        browser = p.chromium.launch(
            headless=False
        )

        print("Context作成")

        context = browser.new_context(
            http_credentials={
                "username": req.basic_username,
                "password": req.basic_password,
            }
        )

        print("Page作成")

        page = context.new_page()

        print("Basic認証付きでアクセス")

        page.goto(
            "https://eba-report.xyz/index"
        )

        print("ログイン画面表示")

        page.locator(
            "input[name='login_id']"
        ).fill(req.portal_username)

        print("ログインID入力完了")

        page.locator(
            "input[name='login_pass']"
        ).fill(req.portal_password)

        print("パスワード入力完了")

        page.locator(
            "button[name='accept']"
        ).click()

        print("ログインボタン押下")

        page.wait_for_load_state("networkidle")

        print("現在URL")
        print(page.url)

        if "top" in page.url:
            print("ログイン成功")
            browser.close()
            return True

        print("ログイン失敗")

        browser.close()

        return False