from axe_core_python.sync_playwright import Axe

IGNORED_RULES = {"color-contrast", "button-name"}

def test_a11y_home(playwright, base_url):
    browser = playwright.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(base_url, wait_until="domcontentloaded")

    axe = Axe()
    results = axe.run(page)
    violations = results.get("violations", [])
    critical = [v for v in violations if v.get('impact') == 'critical' and v.get('id') not in IGNORED_RULES]
    assert not critical, f"Kritik a11y ihlalleri: {[v['id'] for v in critical]}"

    browser.close()

