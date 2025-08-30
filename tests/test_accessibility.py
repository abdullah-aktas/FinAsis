from axe_core_python.sync_playwright import Axe

def test_a11y_home(playwright, base_url):
    browser = playwright.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(base_url, wait_until="domcontentloaded")

    axe = Axe(page)
    results = axe.run()
    violations = results.get("violations", [])
    assert not violations, f"Erişilebilirlik ihlalleri: {[v['id'] for v in violations]}"

    browser.close()

