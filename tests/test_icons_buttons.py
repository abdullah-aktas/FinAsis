import pytest
try:
    import playwright  # type: ignore  # noqa: F401
    import pytest_playwright  # type: ignore  # noqa: F401
    _PW_READY = True
except Exception:
    _PW_READY = False

@pytest.mark.skipif(not _PW_READY, reason="playwright not installed")
def test_images_and_icons_load(playwright, base_url):
    browser = playwright.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(base_url, wait_until="networkidle")

    imgs = page.locator("img").all()
    for i, img in enumerate(imgs):
        ok = page.evaluate("(el) => (el.complete && el.naturalWidth > 0)", img)
        assert ok, f"Bozuk <img> #{i} src={img.get_attribute('src')}"

    icons = page.locator("link[rel*='icon']").all()
    for ln in icons:
        href = ln.get_attribute("href")
        if not href:
            continue
        url = href if href.startswith("http") else f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        resp = page.request.get(url)
        assert resp.ok, f"Favicon yüklenemedi: {href}"

    browser.close()

