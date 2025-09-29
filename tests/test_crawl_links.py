import urllib.parse
import pytest
try:
    import playwright  # type: ignore  # noqa: F401
    import pytest_playwright  # type: ignore  # noqa: F401
    _PW_OK = True
except Exception:
    _PW_OK = False

MAX_PAGES = 200

def normalize(base, href):
    return urllib.parse.urljoin(base, (href or '').split('#')[0])

@pytest.mark.parametrize("start_path", ["/", "/sitemap.xml"])
@pytest.mark.skipif(not _PW_OK, reason="playwright not installed")
def test_crawl_no_404(playwright, base_url, start_path):
    browser = playwright.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()

    to_visit = {urllib.parse.urljoin(base_url, start_path)}
    visited = set()
    bad = []

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        assert resp, f"Yanıt yok: {url}"
        status = resp.status
        if status >= 400:
            bad.append((url, status))
            continue

        anchors = page.locator("a[href]").all()
        for a in anchors:
            href = a.get_attribute("href")
            if not href or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            full = normalize(base_url, href)
            if full.startswith(base_url):
                to_visit.add(full)

    browser.close()
    assert not bad, f"Kırık/kötü sayfalar: {bad}"

