import subprocess
import time
import urllib.request
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"


def wait_for_server(url, timeout=30, interval=0.5):
    """Poll the server until it responds or timeout is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except (ConnectionRefusedError, OSError):
            time.sleep(interval)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s")


@pytest.fixture(scope="session", autouse=True)
def django_server():
    proc = subprocess.Popen(
        ["python", "manage.py", "runserver", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    wait_for_server(BASE_URL)
    yield
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=5)
    if stderr:
        print(f"[django-server stderr]\n{stderr.decode()}")


@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        pg = context.new_page()
        yield pg
        context.close()
        browser.close()