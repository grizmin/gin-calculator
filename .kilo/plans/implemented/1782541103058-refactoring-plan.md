# Gin Calculator Refactoring Plan

## Plan 1: Extract Shared Ingredient-Creation Helpers

### Current Issue
Four locations independently implement an identical ingredient-creation loop (get-or-create `Ingredient`, then create `RecipeIngredient`), and three of them duplicate a superuser-lookup pattern:
- `calculator/management/commands/create_default_recipe.py`
- `calculator/management/commands/create_custom_default_recipe.py`
- `calculator/management/commands/create_famous_recipes.py`
- `docker-setup.py`

### Files
| Action | Path |
|--------|------|
| NEW | `calculator/management/commands/_helpers.py` |
| EDIT | `calculator/management/commands/create_default_recipe.py` |
| EDIT | `calculator/management/commands/create_custom_default_recipe.py` |
| EDIT | `calculator/management/commands/create_famous_recipes.py` |
| EDIT | `docker-setup.py` |

### Change Details

**Step 1a**: Create `calculator/management/commands/_helpers.py` with two functions:

```python
from django.contrib.auth.models import User
from calculator.models import Ingredient, RecipeIngredient


def get_superuser(cmd):
    """Return the first superuser, or print a warning and return None."""
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        cmd.stdout.write(cmd.style.WARNING(
            'No superuser found. Please create a superuser first with: '
            'python manage.py createsuperuser'
        ))
    return admin_user


def create_recipe_ingredients(recipe, ingredients_data):
    """Create RecipeIngredient rows for the given recipe.
    
    ingredients_data: list of dicts with keys: name, amount, order,
                      and optionally is_optional (default False), notes (default '').
    """
    created = 0
    for data in ingredients_data:
        ingredient, _ = Ingredient.objects.get_or_create(name=data['name'])
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=data['amount'],
            order=data.get('order', 0),
            is_optional=data.get('is_optional', False),
            notes=data.get('notes', ''),
        )
        created += 1
    return created
```

**Step 1b**: Update `create_default_recipe.py`:
- Remove `import json` and `import os` (unused)
- Replace `from django.contrib.auth.models import User` + `from calculator.models import Ingredient, RecipeIngredient` with `from calculator.models import GinRecipe`
- Import and use `get_superuser` and `create_recipe_ingredients` from `.helpers`
- Remove the manual ingredient loop (lines 48-56)

**Step 1c**: Update `create_custom_default_recipe.py`:
- Same import changes
- Remove manual ABV validation (lines 38-42) — the model's `MinValueValidator`/`MaxValueValidator` handles this
- Use helper functions

**Step 1d**: Update `create_famous_recipes.py`:
- Same import changes
- Use helper functions
- (Plan 3 covers the path/IMAGE_URLS changes separately)

**Step 1e**: Update `docker-setup.py`:
- Import `create_recipe_ingredients` from `calculator.management.commands._helpers` (using full path since it's not a management command)
- Replace manual ingredient loop (lines 58-66)

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py check
python manage.py test calculator
```

**Visual test:**
```bash
# Verify each seed command still works
python manage.py create_default_recipe
# Should print: "Default recipe 'Classic London Dry' already exists." (or create it)

python manage.py create_famous_recipes
# Should print success for each recipe or "already exists" for existing ones

python manage.py create_custom_default_recipe --name "Test Refactor" --abv-percentage 45
# Should create a new recipe with the helper

# Load page and verify default recipe still loads with ingredients
open http://localhost:8000
```

---

## Plan 2: Extract Inline JavaScript to Static Files

### Current Issue
`calculator/templates/calculator/index.html` is 858 lines, with 547 lines of inline JavaScript (lines 310-856). This is un-cacheable, untestable in isolation, and makes the template hard to read.

### Files
| Action | Path |
|--------|------|
| NEW | `calculator/static/calculator/js/theme.js` |
| NEW | `calculator/static/calculator/js/state.js` |
| NEW | `calculator/static/calculator/js/calculator.js` |
| NEW | `calculator/static/calculator/js/render.js` |
| NEW | `calculator/static/calculator/js/still-dropdown.js` |
| NEW | `calculator/static/calculator/js/main.js` |
| EDIT | `calculator/templates/calculator/index.html` |

### Change Details

**Step 2a**: Create `calculator/static/calculator/js/theme.js` (~30 lines):
- Extract `initTheme()`, `updateThemeIcon()`, `toggleTheme()` functions
- Wrap in IIFE, attach `toggleTheme` to `window` for the button handler
- Attach `initTheme` to `DOMContentLoaded`

**Step 2b**: Create `calculator/static/calculator/js/state.js` (~45 lines):
- Extract `saveState()`, `restoreState()`, `getCurrentMode()`, `setMode()` functions
- Attach to `window` (needed by event handlers in main.js)

**Step 2c**: Create `calculator/static/calculator/js/calculator.js` (~85 lines):
- Extract `calculateLocally()`, `calculateDistill()`, `parseVariation()`, `debounce()` functions
- Attach to `window` (needed by event handlers)

**Step 2d**: Create `calculator/static/calculator/js/render.js` (~75 lines):
- Extract `renderResults()`, `renderRecipeImage()`, `renderRecipeDescription()`, `escHtml()`

**Step 2e**: Create `calculator/static/calculator/js/still-dropdown.js` (~70 lines):
- Extract `STILL_PRESETS` object (remove `{% static %}` tags, use relative paths)
- Extract `renderStillDropdown()`, `selectStill()`, `openStillDropdown()`, `closeStillDropdown()`, `toggleStillDropdown()`
- **Critical:** Replace `{% static "calculator/images/still-vevor.jpg" %}` with hardcoded paths like `/static/calculator/images/still-vevor.jpg` (Django serves static files at `STATIC_URL`)

**Step 2f**: Create `calculator/static/calculator/js/main.js` (~80 lines):
- Extract `onRecipeChange()`, `loadRecipeDetails()`, `positionTooltip()`, `hideTooltip()`
- All event wiring (mode buttons, spirit type radios, input listeners, dropdown listeners, recipe change, theme toggle, language toggle)
- `window.addEventListener('load', ...)` entry point

**Step 2g**: Edit `calculator/templates/calculator/index.html`:
- Remove lines 310-856 (all inline JS)
- Keep only the bootstrap block:
  ```html
  <script>
    window.__lang = '{{ lang }}';
    window.__t = {
      en: { /* existing 24 keys */ },
      bg: { /* existing 24 keys */ }
    };
    function t(key) {
      var dict = window.__t[window.__lang] || window.__t['en'];
      return dict[key] || key;
    }
  </script>
  ```
- Add script tags at end of `<body>`:
  ```html
  <script src="{% static 'calculator/js/theme.js' %}"></script>
  <script src="{% static 'calculator/js/state.js' %}"></script>
  <script src="{% static 'calculator/js/calculator.js' %}"></script>
  <script src="{% static 'calculator/js/render.js' %}"></script>
  <script src="{% static 'calculator/js/still-dropdown.js' %}"></script>
  <script src="{% static 'calculator/js/main.js' %}"></script>
  ```
- Remove the language toggle's `saveState()` + `window.location.reload()` logic (this is already handled by the Django template — the reload renders the new language. The saveState before reload is already in state.js).

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py collectstatic --noinput  # Ensure static files are collected
python manage.py check
python -m pytest tests/  # Playwright UI tests verify the page works end-to-end
```

**Visual test** (after `python manage.py runserver`):
1. **Page loads**: Open http://localhost:8000 — page should render identically to before
2. **Recipe dropdown**: Select a different recipe — description, image, and target ABV should update
3. **Calculator**: Change volume to 2L, spirit ABV to 96, target ABV to 40 — results should appear with ingredient amounts scaled 2x
4. **Mode switch**: Click "Distill" tab — distill panel appears with still dropdown
5. **Still dropdown**: Click dropdown, select "Селски 100L" — inputs should populate and results update
6. **Theme toggle**: Click moon/sun icon — theme should toggle between light/dark
7. **Language switch**: Click "EN" button — page should reload in Bulgarian (or English)
8. **State persistence**: Change values, switch mode, reload page — state should be restored
9. **Error messages**: Set maceration ABV higher than spirit ABV — should show error "Maceration ABV must be lower..."
10. **Variation pills**: For ingredients with ±X% notes — clicking min/base/max pills should change displayed amount
11. **Browser devtools**: Open Network tab — JS files should load from `/static/calculator/js/` with proper cache headers

---

## Plan 3: Move Image URLs into Fixture JSON + Fix Path Construction

### Current Issue
`create_famous_recipes.py` hardcodes 8 image URLs in an `IMAGE_URLS` dict (lines 20-29) and constructs the fixture path with a fragile 4-level `os.path.dirname()` chain (lines 32-33). The AGENTS.md notes "a known fixture-path bug under investigation."

### Files
| Action | Path |
|--------|------|
| EDIT | `calculator/fixtures/famous_gin_recipes.json` |
| EDIT | `calculator/management/commands/create_famous_recipes.py` |

### Change Details

**Step 3a**: Add `"image_url"` field to each recipe in the fixture JSON:

```json
{
  "name": "Tanqueray London Dry",
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Tanqueray_bottle.JPG",
  ...
}
```

For all 8 recipes, add the `image_url` key with the URL currently in the `IMAGE_URLS` dict. Insert between `"name"` and `"description"` for consistency.

**Step 3b**: Update `create_famous_recipes.py`:
- Remove the `IMAGE_URLS` dict (lines 20-29)
- Replace path construction (lines 32-33) with:
  ```python
  from pathlib import Path
  fixture_path = Path(__file__).resolve().parent.parent.parent.parent / 'calculator' / 'fixtures' / 'famous_gin_recipes.json'
  ```
- Remove the image backfill logic (lines 41-54) — since image URLs are now in the fixture, this is unnecessary
- Update recipe creation to use `recipe_data.get('image_url', '')` instead of `IMAGE_URLS.get(recipe_data['name'], "")`

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py test calculator
# Specifically: test_creates_all_8_recipes, test_idempotent, test_tanqueray_has_4_ingredients,
#              test_monkey47_has_47_ingredients, test_fixture_abv_volume_is_self_consistent
```

**Visual test:**
```bash
# Delete existing famous recipes (via admin or shell), then:
python manage.py create_famous_recipes
# Should print success for all 8 recipes

# Open the page, select each recipe from the dropdown:
# Tanqueray London Dry → should show Tanqueray bottle image
# Hendrick's → should show Hendrick's image
# Bombay Sapphire → should show Bombay Sapphire image
# ... etc for all 8

# Also verify in admin:
open http://localhost:8000/admin/calculator/ginrecipe/
# Edit any famous recipe, verify image_url field is populated
```

---

## Plan 4: Remove Dead Code

### Current Issue
Three pieces of code serve no purpose:
1. `BREWING_LOSS_PERCENTAGE = 10` in `gin_calculator/settings.py` (line 133) — never imported or used
2. `calculator/management/commands/delete_orphaned_recipes.py` — one-time cleanup with hardcoded IDs `[3, 4, 5]`
3. `import json` and `import os` in `create_default_recipe.py` (lines 4-5) — never used in that file

### Files
| Action | Path |
|--------|------|
| EDIT | `gin_calculator/settings.py` |
| DELETE | `calculator/management/commands/delete_orphaned_recipes.py` |
| EDIT | `calculator/management/commands/create_default_recipe.py` |

### Change Details

**Step 4a**: Remove line 133 from `gin_calculator/settings.py`:
```python
BREWING_LOSS_PERCENTAGE = 10  # % volume lost during distillation
```

**Step 4b**: Delete `calculator/management/commands/delete_orphaned_recipes.py`. (Also delete its `__pycache__` compiled version if present.)

**Step 4c**: Remove lines 4-5 from `create_default_recipe.py`:
```python
import json
import os
```
(Note: Plan 1 already handles this in its refactor. If Plan 1 executes first, this step is a no-op for `create_default_recipe.py`.)

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py check
python manage.py test calculator
```

**Visual test:**
```bash
python manage.py runserver
# Verify:
# 1. App loads at http://localhost:8000
# 2. Admin works at http://localhost:8000/admin/
# 3. python manage.py create_default_recipe still works
# 4. python manage.py shows no "delete_orphaned_recipes" command
python manage.py | grep delete_orphaned_recipes
# Should output nothing (command no longer exists)
```

---

## Plan 5: Add Missing Admin Fields

### Current Issue
`GinRecipeAdmin.fieldsets` in `calculator/admin.py` omits `image_url` and `water_for_maceration`. Both fields exist on the model but cannot be edited through the admin UI.

### Files
| Action | Path |
|--------|------|
| EDIT | `calculator/admin.py` |

### Change Details

Edit `GinRecipeAdmin.fieldsets` in `admin.py`:

```python
fieldsets = (
    ('Basic Information', {
        'fields': ('name', 'description', 'image_url')
    }),
    ('Recipe Details', {
        'fields': ('base_volume', 'abv_volume', 'target_abv_percentage', 'water_for_maceration')
    }),
    ('Settings', {
        'fields': ('is_active', 'is_default')
    }),
    ('Metadata', {
        'fields': ('created_by', 'created_at', 'updated_at'),
        'classes': ('collapse',)
    })
)
```

- Add `'image_url'` to the `'Basic Information'` fieldset
- Add `'water_for_maceration'` to the `'Recipe Details'` fieldset

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py check
```

**Visual test:**
```bash
python manage.py runserver
# Open admin: http://localhost:8000/admin/calculator/ginrecipe/
# Click "Add Gin Recipe" (or edit an existing one)
# Verify:
# 1. "Image URL" field appears under "Basic Information"
# 2. "Water for maceration" field appears under "Recipe Details"
# 3. Both fields accept input and save correctly
# 4. After saving, the values persist on edit
```

---

## Plan 6: Extract Duplicated Test Constants

### Current Issue
The list of 8 famous recipe names appears in 3 full-list copies across `tests/test_calculator_views.py` (lines 153-163, 171-181, 223-233). `BASE_URL` is defined independently in both `tests/conftest.py` and `tests/test_ui.py`.

### Files
| Action | Path |
|--------|------|
| EDIT | `tests/test_calculator_views.py` |
| EDIT | `tests/test_ui.py` |

### Change Details

**Step 6a**: Add module-level constant at the top of `tests/test_calculator_views.py` (after imports, before class definitions):

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

Replace all 3 inline copies of this list with `FAMOUS_RECIPE_NAMES`:
- `test_creates_all_8_recipes`: `GinRecipe.objects.filter(name__in=FAMOUS_RECIPE_NAMES).delete()` and `.filter(name__in=FAMOUS_RECIPE_NAMES)`
- `test_fixture_abv_volume_is_self_consistent`: same pattern

**Step 6b**: In `tests/test_ui.py`, replace `BASE_URL = "http://127.0.0.1:8000"` with `from tests.conftest import BASE_URL`:

```python
from tests.conftest import BASE_URL
```

### Verification

**Code test:**
```bash
pyenv activate gin
python manage.py test calculator
python -m pytest tests/ -x
```

**Visual test:**
No visual component — this is purely a test refactor. Verify all tests pass with identical assertions.

---

## Plan 7: Replace `time.sleep(3)` with HTTP Readiness Poll

### Current Issue
`tests/conftest.py` uses `time.sleep(3)` (line 16) to wait for the Django dev server, with no actual readiness check. On slow CI this can be insufficient; on fast machines it wastes time.

### Files
| Action | Path |
|--------|------|
| EDIT | `tests/conftest.py` |

### Change Details

Replace the `django_server` fixture:

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
    # Poll until the server responds or timeout
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

Key changes:
- Add `import urllib.request`
- Replace `time.sleep(3)` with a polling loop (max 30s timeout, 0.5s interval)
- Add `proc.terminate()` + `proc.wait()` on timeout to clean up before raising
- Add `BASE_URL` constant (already present, reused)

### Verification

**Code test:**
```bash
pyenv activate gin
python -m pytest tests/ -x -v
# Verify: tests start, server is detected as ready, tests pass
```

**Visual test:**
```bash
# Run tests and observe timing:
time python -m pytest tests/ -x
# Should complete in roughly the same time or faster (no fixed 3s wait)

# Simulate slow startup by temporarily adding a delay to manage.py or 
# just verify the timeout works by checking the error message format:
# If server fails to start, should see: "Django dev server did not start within 30s"
```

---

## Execution Order & Dependencies

Plans 1-7 are independent and can run in any order with one exception: Plan 2 (JS extraction) should run LAST because it's the highest-risk change and benefits from all other refactors being stable first.

| Order | Plan | Risk | Depends On |
|-------|------|------|------------|
| 1 | Plan 4: Dead code removal | Low | None |
| 2 | Plan 5: Admin fields | Low | None |
| 3 | Plan 6: Test constants | Low | None |
| 4 | Plan 7: HTTP readiness poll | Low-Medium | None |
| 5 | Plan 1: Shared helpers | Medium | None (but Plan 4 removes imports from create_default_recipe.py) |
| 6 | Plan 3: Fixture image URLs + pathlib | Medium | Plan 1 (uses same helper after refactor) |
| 7 | Plan 2: JS extraction | High | Plans 1-6 (everything else stable first) |

After each plan, run the full verification suite:
```bash
python manage.py check && python manage.py test calculator && python -m pytest tests/
```
