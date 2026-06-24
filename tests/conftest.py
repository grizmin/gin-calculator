import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def django_server():
    proc = subprocess.Popen(
        ["python", "manage.py", "runserver", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        pg = context.new_page()
        yield pg
        context.close()
        browser.close()