# Plan: Playwright UI Tests + Bug Fixes

## Executor Rules

> 1. Execute **one step at a time**. Do not begin step N+1 until the verify command for step N passes.
> 2. Each step names **exactly one file**. Do not touch any other file in that step.
> 3. If the code contradicts these instructions, **stop and report**. Do not guess.
> 4. Do not make unrequested improvements.
> 5. Run every verify command exactly as written.

---

## Bugs to Fix First

### Bug 1 — Wrong URL in `index.html` JS
`loadRecipeDetails` fetches `/get_recipe/` (underscore) but the Django URL is `/get-recipe/` (hyphen). This means recipe details never load, the `#target_abv` field never pre-fills, and `currentRecipe` is always null.

### Bug 2 — Wrong formula in `views.py`
The current implementation ignores `settings.BREWING_LOSS_PERCENTAGE` entirely.

**Current (wrong):**
```python
spirit_needed = (desired_volume * target_abv_percentage) / input_spirit_abv
water_to_add  = desired_volume - spirit_needed
```

**Correct (from original plan):**
```python
brewing_loss        = settings.BREWING_LOSS_PERCENTAGE / 100
pure_alcohol_needed = round(desired_volume * (target_abv / 100), 3)
spirit_needed       = round(pure_alcohol_needed / (input_spirit_abv / 100) / (1 - brewing_loss), 3)
water_to_add        = round(desired_volume - spirit_needed * (1 - brewing_loss), 3)
```

Expected values for 1.5 L / 96% spirit / 40% target / 10% loss:
- `pure_alcohol_needed = 1.5 × 0.40 = 0.600`
- `spirit_needed = 0.600 / 0.96 / 0.90 = 0.694`
- `water_to_add = 1.5 − 0.694 × 0.90 = 0.875`

The JSON response must return `spirit_needed` and `water_to_add` rounded to **3** decimal places. `scale_factor` rounded to **2**.

---

## Steps

### Step 1 — Fix URL bug in `calculator/templates/calculator/index.html`

In `loadRecipeDetails`, replace:
```js
const response = await fetch('/get_recipe/', {
```
With:
```js
const response = await fetch('/get-recipe/', {
```

**Verify:**
```bash
grep "get.recipe" calculator/templates/calculator/index.html
```
Output must show `/get-recipe/` (hyphen), not `/get_recipe/` (underscore).

---

### Step 2 — Fix formula in `calculator/views.py`

Read the file first.

**A. Ensure this import exists at the top** (it already does but confirm):
```python
from django.conf import settings
```

**B. Replace** the formula block (lines ~46–60). Find these lines:
```python
            input_spirit_abv = float(data.get('input_spirit_abv', 40.0))  # Default to 40% if not provided
            target_abv_percentage = float(data.get('target_abv', recipe.target_abv_percentage or 40.0))
            
            # Calculate spirit needed and water to add based on the formula
            # spirit_needed = (desired_volume * target_abv_percentage) / input_spirit_abv
            # water_to_add = desired_volume - spirit_needed
            
            # The logic is more complex for accurate ABV calculation:
            # We need to ensure that final result matches target_abv_percentage
            # Let's use: target_abv = (spirit_volume * spirit_abv) / total_volume
            # So: spirit_volume = (target_abv * total_volume) / spirit_abv
            
            spirit_needed = (desired_volume * target_abv_percentage) / input_spirit_abv
            water_to_add = desired_volume - spirit_needed
            
            # Scale all ingredients
```

Replace with:
```python
            input_spirit_abv = float(data.get('input_spirit_abv', 96.0))
            target_abv = float(data.get('target_abv', recipe.target_abv_percentage or 40.0))
            brewing_loss = settings.BREWING_LOSS_PERCENTAGE / 100

            pure_alcohol_needed = round(desired_volume * (target_abv / 100), 3)
            spirit_needed = round(pure_alcohol_needed / (input_spirit_abv / 100) / (1 - brewing_loss), 3)
            water_to_add = round(desired_volume - spirit_needed * (1 - brewing_loss), 3)

            # Scale all ingredients
```

**C. Update the JsonResponse** to use `target_abv` (local var) not `recipe.target_abv_percentage`:
```python
            return JsonResponse({
                'success': True,
                'recipe_name': recipe.name,
                'recipe_description': recipe.description,
                'scaled_ingredients': scaled_ingredients,
                'spirit_needed': spirit_needed,
                'water_to_add': water_to_add,
                'target_abv_percentage': target_abv,
                'input_spirit_abv': input_spirit_abv,
                'scale_factor': round(scale_factor, 2),
            })
```

Also remove the two stale comment lines about "Calculate spirit needed and water to add" and "Note: This logic assumes..." if they remain.

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

**Manual verify** — with the dev server running, POST to the calculate endpoint:
```bash
curl -s -X POST http://127.0.0.1:8000/calculate/ \
  -H "Content-Type: application/json" \
  -d '{"volume": 1.5, "recipe_id": 1, "input_spirit_abv": 96, "target_abv": 40}' | python -m json.tool
```
Must return `spirit_needed` ≈ `0.694` and `water_to_add` ≈ `0.875`.

---

### Step 3 — Create `tests/__init__.py`

Create an empty file at `tests/__init__.py`.

**Verify:**
```bash
ls tests/
```
Must show `__init__.py`.

---

### Step 4 — Create `tests/conftest.py`

Create `tests/conftest.py` with this exact content:

```python
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
```

**Verify:**
```bash
python -c "import tests.conftest; print('ok')"
```
Must print `ok`.

---

### Step 5 — Create `tests/test_ui.py`

Create `tests/test_ui.py` with this exact content:

```python
import pytest
from playwright.sync_api import expect

BASE_URL = "http://127.0.0.1:8000"


def test_page_loads(page):
    """Home page returns 200 and shows the calculator."""
    page.goto(BASE_URL)
    expect(page.locator("h1")).to_contain_text("Gin")


def test_input_fields_present(page):
    """All three inputs are visible: volume, spirit ABV, target ABV."""
    page.goto(BASE_URL)
    expect(page.locator("#volume")).to_be_visible()
    expect(page.locator("#input_spirit_abv")).to_be_visible()
    expect(page.locator("#target_abv")).to_be_visible()


def test_recipe_dropdown_populated(page):
    """Recipe dropdown contains at least one option with a real value."""
    page.goto(BASE_URL)
    options = page.locator("#recipe_select option")
    expect(options.first).to_be_visible()
    count = options.count()
    assert count >= 1


def test_target_abv_prefills_from_recipe(page):
    """After page load, target ABV field is pre-filled from the default recipe (≥ 10)."""
    page.goto(BASE_URL)
    page.wait_for_function("document.getElementById('target_abv').value !== ''")
    value = page.input_value("#target_abv")
    assert float(value) >= 10.0, f"Expected target_abv >= 10, got {value}"


def test_calculate_formula(page):
    """1.5 L / 96% spirit / 40% target → spirit ≈ 0.694 L, water ≈ 0.875 L."""
    page.goto(BASE_URL)
    page.wait_for_function("document.getElementById('target_abv').value !== ''")

    page.fill("#volume", "1.5")
    page.fill("#input_spirit_abv", "96")
    page.fill("#target_abv", "40")
    page.click(".calculate-btn")

    page.wait_for_selector("#results.show")

    spirit = page.inner_text("#spirit-needed")
    water  = page.inner_text("#water-to-add")

    assert "0.694" in spirit, f"Wrong spirit value: {spirit!r}"
    assert "0.875" in water,  f"Wrong water value: {water!r}"
```

**Verify:**
```bash
pytest tests/test_ui.py -v
```
All 5 tests must pass. The `django_server` fixture starts and stops the dev server automatically — do **not** start `runserver` manually before running pytest.

---

## Risks

- `test_target_abv_prefills_from_recipe` uses `wait_for_function` which polls until the field has a value. If `/get-recipe/` returns an error, the field stays empty and the test times out. The Step 1 URL fix is a prerequisite.
- The `django_server` fixture binds to port 8000. If something else is on port 8000 when pytest runs, the server will fail to start silently. The executor must ensure port 8000 is free before running pytest.
- `--noreload` is required in the subprocess call so Django doesn't spawn a second watcher process that outlives the test session.

## Validation Checklist

- [ ] `grep "get.recipe" index.html` → shows `/get-recipe/` (hyphen)
- [ ] `python manage.py check` passes
- [ ] `curl` to `/calculate/` returns `spirit_needed=0.694`, `water_to_add=0.875`
- [ ] `pytest tests/test_ui.py -v` → 5 passed
