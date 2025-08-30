import os
import pytest

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

