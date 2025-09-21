import os
import pytest

# Allow Django DB operations in async contexts used by Playwright during teardown
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

@pytest.fixture(scope="session")
def base_url(live_server):
    override = os.getenv("BASE_URL")
    return override or live_server.url

