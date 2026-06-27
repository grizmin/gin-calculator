# Refactor D: Test Constants + HTTP Readiness Poll

Prerequisite: Plan C complete and green.

Run after each step: `pyenv activate gin && python manage.py check && python manage.py test calculator && python -m pytest tests/`

---

## Context

- The list of 8 famous recipe names is duplicated 3 times in `tests/test_calculator_views.py`.
- `BASE_URL` is defined independently in both `tests/conftest.py` and `tests/test_ui.py`.
- `tests/conftest.py` uses `time.sleep(3)` with no readiness check — brittle on slow machines.

---

## Step 1

**File:** `tests/test_calculator_views.py`  
**Change:** Add a module-level constant after the imports:

```python
FAMOUS_RECIPE_NAMES = [
    'Tanqueray London Dry',
    "Hendrick's",
    'Bombay Sapphire',
    'Beefeater London Dry',
    'Aviation American Gin',
    "Gordon's London Dry",
    'Monkey 47 Schwarzwald Dry Gin',
    'Sipsmith London Dry',
]
```

Replace all 3 inline copies of this list in the file with `FAMOUS_RECIPE_NAMES`.  
**Verify:** `python manage.py test calculator` — same number of tests pass, no regressions.

---

## Step 2

**File:** `tests/test_ui.py`  
**Change:** Remove the `BASE_URL = "http://127.0.0.1:8000"` line and replace it with `from tests.conftest import BASE_URL` (or `from conftest import BASE_URL` depending on how pytest resolves the import — check the existing imports in the file and match the style).  
**Verify:** `python -m pytest tests/ -x` — all UI tests pass.

---

## Step 3

**File:** `tests/conftest.py`  
**Change:** Replace the `time.sleep(3)` wait with an HTTP polling loop:

```python
import subprocess
import time
import urllib.request
import pytest

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def django_server():
    proc = subprocess.Popen(
        ["python", "manage.py", "runserver", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    timeout = 30
    start = time.monotonic()
    while True:
        try:
            urllib.request.urlopen(BASE_URL)
            break
        except Exception:
            if time.monotonic() - start > timeout:
                proc.terminate()
                proc.wait()
                raise RuntimeError("Django dev server did not start within 30s")
            time.sleep(0.5)
    yield
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=5)
    if stderr:
        print(f"[django-server stderr]\n{stderr.decode()}")
```

Keep `BASE_URL` defined here (it is the single source of truth after Step 2).  
**Verify:** `python -m pytest tests/ -x -v` — server starts, tests pass. Timing should be similar or faster than before.

---

## Step 4 — Full gate

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`  
All must pass before moving to Plan E.
