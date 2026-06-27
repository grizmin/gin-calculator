# Remove obsolete `/calculate/` backend endpoint

## Context
The frontend uses `calculateLocally()` in `index.html` for all math. The backend `calculate` view, its URL route, and all tests exercising it are dead code. The `get_recipe` endpoint is still live and must not be touched.

## Steps

### 1. `calculator/views.py` — Remove `calculate()` function
- Delete lines 24–93 (the `@csrf_exempt` decorator + `calculate` function).
- Keep `index`, `get_recipe`, and all imports that remain in use.
- **Verify:** `python manage.py check` passes; `grep -n "def calculate" calculator/views.py` returns nothing.

### 2. `calculator/urls.py` — Remove `calculate/` route
- Delete: `path('calculate/', views.calculate, name='calculate'),`
- **Verify:** file has exactly 2 `path()` entries (`index` and `get-recipe/`).

### 3. `calculator/tests.py` — Remove `test_calculate_endpoint`
- Delete `test_calculate_endpoint` method (lines 63–87) from `CalculatorViewsTest`.
- Leave `test_get_recipe_endpoint` and `test_target_abv_prefills_from_recipe` intact.
- Leave `FamousRecipesCommandTest` class intact.
- **Verify:** `python manage.py test calculator --verbosity 2` — all remaining tests pass, no reference to `calculate` endpoint.

### 4. `tests/test_calculator_views.py` — Remove calculate endpoint tests
- Delete `test_calculate_endpoint` (lines 91–140) and `test_calculate_with_scaled_volume` (lines 142–170) from `CalculatorViewsTest`.
- Leave all other tests intact (`test_get_recipe_endpoint`, `test_target_abv_prefills_from_recipe`, `test_ingredient_model_relationship`, `test_invalid_recipe_id`, `FamousRecipesCommandTest`).
- **Verify:** `python manage.py test tests.test_calculator_views --verbosity 2` passes.

### 5. `test-docker.sh` — Remove `/calculate/` HTTP check
- Delete line 55: `test_http "http://localhost:8000/calculate/" "405"`
- **Verify:** `bash -n test-docker.sh` (syntax check only; do not run against a live container).

## Final validation
```bash
python manage.py check
python manage.py test calculator tests.test_calculator_views --verbosity 2
pytest tests/test_ui.py --verbosity 2
```
All must pass with zero failures.
