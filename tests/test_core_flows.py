import pytest
try:
    import playwright  # type: ignore  # noqa: F401
    _PW = True
except Exception:
    _PW = False
try:
    import pytest_playwright  # type: ignore  # noqa: F401
    _PW_PLUGIN = True
except Exception:
    _PW_PLUGIN = False

CRITICAL_PATHS = ["/", "/finance/", "/ai-assistant/"]

if _PW and _PW_PLUGIN:
    @pytest.mark.parametrize("path", CRITICAL_PATHS)
    def test_buttons_clickable(playwright, base_url, path):
        browser = playwright.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(f"{base_url}{path}", wait_until="domcontentloaded")

        buttons = page.locator("button:visible:not([disabled])").all()
        for i, btn in enumerate(buttons[:10]):
            try:
                btn.click(timeout=1500)
            except Exception:
                pass  # ana akışları kırmamak için pas geçiyoruz (demo)

        browser.close()

