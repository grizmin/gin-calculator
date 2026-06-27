# Plan: Spirit Volume UI Inputs

## Executor Rules

> **Read these before starting. Follow them without exception.**
>
> 1. Execute **one step at a time**. Do not begin step N+1 until the verify command for step N passes.
> 2. Each step names **exactly one file**. Do not touch any other file in that step.
> 3. If the code in a file contradicts these instructions, **stop and report the conflict**. Do not resolve it by guessing.
> 4. Do not make unrequested improvements (UI polish, refactors, new features).
> 5. Run every verify command exactly as written. Do not skip or substitute.

---

## Goal

Add two configurable inputs to the calculator UI:

- **Spirit ABV (%)** — the alcohol strength of the input spirit (UI-only, default 96, not stored)
- **Target Gin ABV (%)** — the desired strength of the finished gin (stored per-recipe as `target_abv_percentage`, pre-fills from selected recipe)

Wire both values through the `calculate` view using a spirit/water formula. Show `spirit_needed` and `water_to_add` in the results panel.

---

## Decisions

| Decision | Value |
|---|---|
| Field name | `abv_percentage` → `target_abv_percentage` |
| Validators | `MinValueValidator(10.0)`, `MaxValueValidator(99.0)` |
| Default | `40.0` |
| Brewing loss constant | `BREWING_LOSS_PERCENTAGE = 10` in `settings.py` |
| Input spirit ABV | UI-only, default 96, not stored |
| `abv_volume` field | Keep unchanged — legacy field, not used in formula |
| Broken `0002` migration | Delete it; regenerate cleanly |
| `water_to_add` negative | No guard — return the negative value as-is |
| Rounding | `spirit_needed`, `water_to_add` → 3 decimal places; `scale_factor` → 2 |

---

## Formula

```
pure_alcohol_needed = desired_volume × (target_abv / 100)
spirit_needed       = pure_alcohol_needed / (input_spirit_abv / 100) / (1 − BREWING_LOSS / 100)
water_to_add        = desired_volume − spirit_needed × (1 − BREWING_LOSS / 100)
```

**Example** — 1.5 L gin at 40% using 96% spirit, 10% loss:
- pure_alcohol_needed = 1.5 × 0.40 = 0.600 L
- spirit_needed = 0.600 / 0.96 / 0.90 = 0.694 L
- water_to_add = 1.5 − 0.694 × 0.90 = 0.875 L

---

## Current State (what is broken / missing)

- `calculator/migrations/0002_add_abv_percentage_field.py` — hand-written, **never applied** to `db.sqlite3`, wrong definition (`null=True`, no validators). Must be deleted.
- `models.py` — has `abv_percentage` with wrong validators (10–99 set in last session; rename and correct to `target_abv_percentage` 10–99).
- `settings.py` — `BREWING_LOSS_PERCENTAGE` missing.
- `views.py` — `calculate` returns `abv_volume`/`abv_percentage`; no spirit formula; does not read `input_spirit_abv` or `target_abv` from POST.
- `index.html` — no spirit ABV input, no target ABV input, results block shows ABV volume not spirit/water.
- `admin.py` — references `abv_percentage`, needs `target_abv_percentage`.
- `create_default_recipe.py` — seeds `abv_percentage=40.0`; must use `target_abv_percentage=40.0`.
- `tests.py` — empty; must be written from scratch.

---

## Steps

### Step 1 — Delete broken migration

**File:** `calculator/migrations/0002_add_abv_percentage_field.py`

Delete this file entirely.

**Verify:**
```bash
ls calculator/migrations/
```
Output must show only `__init__.py`, `0001_initial.py`, and `__pycache__/`. No `0002` file.

---

### Step 2 — `gin_calculator/settings.py`

Add at the bottom of the file (after line 130):

```python
# Brewing configuration
BREWING_LOSS_PERCENTAGE = 10  # % volume lost during distillation
```

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

---

### Step 3 — `calculator/models.py`

Replace the `abv_percentage` field definition with `target_abv_percentage`. Do **not** touch `save()` or any other field.

Replace:
```python
abv_percentage = models.FloatField(
    default=40.0,
    validators=[MinValueValidator(10.0), MaxValueValidator(99.0)],
    help_text="ABV percentage (10–99%). Calculated as (abv_volume / base_volume) * 100"
)
```

With:
```python
target_abv_percentage = models.FloatField(
    default=40.0,
    validators=[MinValueValidator(10.0), MaxValueValidator(99.0)],
    help_text="Target ABV % of the finished gin (10–99%)"
)
```

Place it after the `abv_volume` field. The `abv_volume` field must remain unchanged.

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

---

### Step 4 — Generate migration

Run:
```bash
python manage.py makemigrations calculator --name ginrecipe_target_abv_percentage
```

Confirm the generated file `calculator/migrations/0002_ginrecipe_target_abv_percentage.py`:
- Depends on `('calculator', '0001_initial')`
- Renames field from `abv_percentage` to `target_abv_percentage` (or removes old and adds new — either is acceptable)
- Has `default=40.0` and no `null=True`

Then apply:
```bash
python manage.py migrate
```

**Verify:**
```bash
python manage.py migrate
```
Must complete with no errors.

---

### Step 5 — `calculator/admin.py`

Two changes only:

1. `list_display`: replace `'abv_percentage'` with `'target_abv_percentage'`
2. `fieldsets` `'Recipe Details'` tuple: replace `'abv_percentage'` with `'target_abv_percentage'`

Result:
```python
list_display = ['name', 'base_volume', 'abv_volume', 'target_abv_percentage', 'is_active', 'is_default', 'created_by', 'created_at']

('Recipe Details', {
    'fields': ('base_volume', 'abv_volume', 'target_abv_percentage')
}),
```

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

---

### Step 6 — `calculator/views.py`

Two sub-changes in this file. Make both in one edit but read the file first.

**A. Add import at top:**
```python
from django.conf import settings
```

**B. Replace the `calculate` view's response block.**

After `scale_factor` is computed and `scaled_ingredients` is built, replace the existing `scaled_abv_volume` line and the `return JsonResponse(...)` block with:

```python
input_spirit_abv = float(data.get('input_spirit_abv', 96.0))
target_abv = float(data.get('target_abv', recipe.target_abv_percentage))
brewing_loss = settings.BREWING_LOSS_PERCENTAGE / 100

pure_alcohol_needed = round(desired_volume * (target_abv / 100), 3)
spirit_needed = round(pure_alcohol_needed / (input_spirit_abv / 100) / (1 - brewing_loss), 3)
water_to_add = round(desired_volume - spirit_needed * (1 - brewing_loss), 3)

return JsonResponse({
    'success': True,
    'recipe_name': recipe.name,
    'recipe_description': recipe.description,
    'scaled_ingredients': scaled_ingredients,
    'target_abv_percentage': target_abv,
    'input_spirit_abv': input_spirit_abv,
    'spirit_needed': spirit_needed,
    'water_to_add': water_to_add,
    'scale_factor': round(scale_factor, 2),
})
```

**C. Update `get_recipe` view** — in the returned recipe dict, replace:
```python
'abv_percentage': recipe.abv_percentage or 0,
```
with:
```python
'target_abv_percentage': recipe.target_abv_percentage,
```
Keep `'abv_volume': recipe.abv_volume` unchanged.

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

---

### Step 7 — `calculator/management/commands/create_default_recipe.py`

In `GinRecipe.objects.create(...)`, replace `abv_percentage=40.0` with `target_abv_percentage=40.0`.

Remove the line `abv_volume = (abv_percentage * base_volume) / 100` and the local variable `abv_percentage`. Set `abv_volume=1.15` (restoring the original seed value — this is a legacy field).

Result for the create call:
```python
recipe = GinRecipe.objects.create(
    name="Classic London Dry",
    description="A traditional London Dry gin recipe with juniper, coriander, and complementary botanicals.",
    base_volume=1.0,
    abv_volume=1.15,
    target_abv_percentage=40.0,
    is_active=True,
    is_default=True,
    created_by=admin_user
)
```

**Verify:**
```bash
python manage.py check
```
Must pass with no errors.

---

### Step 8 — `calculator/templates/calculator/index.html`

Four sub-changes. Read the full file before editing.

**A. Add Spirit ABV input** — inside `.input-section`, after the volume stepper `div.input-group` (after line 401) and before the calculate button:

```html
<div class="input-group">
    <label for="input_spirit_abv">Spirit ABV (%):</label>
    <input type="number" id="input_spirit_abv" value="96" min="10" max="99" step="1">
</div>
```

**B. Add Target Gin ABV input** — immediately after the Spirit ABV input:

```html
<div class="input-group">
    <label for="target_abv">Target Gin ABV (%):</label>
    <input type="number" id="target_abv" value="40" min="10" max="99" step="0.5">
</div>
```

**C. Replace the results `.abv-info` block** (lines 416–420) — replace:

```html
<div class="abv-info">
    <h4>Required ABV Volume</h4>
    <div id="abv-volume" class="abv-amount">0 L</div>
    <p>ABV Percentage: <span id="abv-percentage">0%</span></p>
</div>
```

With:

```html
<div class="abv-info">
    <h4>Spirit & Water Needed</h4>
    <div id="spirit-needed" class="abv-amount">0 L</div>
    <p>Spirit at <span id="result-spirit-abv">96</span>%</p>
    <p>Water to add: <span id="water-to-add">0</span> L</p>
    <p>Target ABV: <span id="result-target-abv">40</span>%</p>
</div>
```

**D. Update JavaScript** — three sub-changes:

1. In `calculateIngredients()`, replace the POST body (currently lines 562–565):
```js
body: JSON.stringify({
    volume: volume,
    recipe_id: parseInt(recipeId),
    input_spirit_abv: parseFloat(document.getElementById('input_spirit_abv').value) || 96,
    target_abv: parseFloat(document.getElementById('target_abv').value) || 40,
})
```

2. In `displayResults(data)`, replace the two ABV lines (currently lines 619–620):
```js
document.getElementById('spirit-needed').textContent = `${data.spirit_needed} L`;
document.getElementById('result-spirit-abv').textContent = data.input_spirit_abv;
document.getElementById('water-to-add').textContent = data.water_to_add;
document.getElementById('result-target-abv').textContent = data.target_abv_percentage;
```
Also remove the variable declarations for `abvVolumeElement` and `abvPercentageElement` at the top of `displayResults`.

3. In `loadRecipeDetails()` success handler, after `currentRecipe = data.recipe`, add:
```js
document.getElementById('target_abv').value = data.recipe.target_abv_percentage;
```

4. In `displayCurrentRecipe(recipe)`, replace the `ABV Volume` line in the template string with:
```js
<strong>Target ABV:</strong> ${recipe.target_abv_percentage}%<br>
<strong>ABV Volume (base ratio):</strong> ${recipe.abv_volume} L
```

**Verify:** Start the dev server (`python manage.py runserver`), open the page. Selecting a recipe must populate the Target Gin ABV field. Clicking Calculate with 1.5 L, 96% spirit, 40% target must show spirit_needed ≈ 0.694 L and water_to_add ≈ 0.875 L in the results panel.

---

### Step 9 — `calculator/tests.py`

Write from scratch. Each test class creates a `User` and `GinRecipe` in `setUp`.

Required test cases:

1. **Model default** — `GinRecipe` created without `target_abv_percentage` defaults to `40.0`.
2. **Model validation low** — `target_abv_percentage=9.0` raises `ValidationError` on `full_clean()`.
3. **Model validation high** — `target_abv_percentage=100.0` raises `ValidationError` on `full_clean()`.
4. **Model validation valid** — `target_abv_percentage=40.0` passes `full_clean()` without error.
5. **`get_recipe` API** — POST to `/get-recipe/` returns `target_abv_percentage` in response JSON.
6. **`calculate` formula correctness** — POST `volume=1.5`, `input_spirit_abv=96`, `target_abv=40` → `spirit_needed` ≈ 0.694 (±0.001), `water_to_add` ≈ 0.875 (±0.001).
7. **`calculate` different spirit ABV** — POST `volume=1.0`, `input_spirit_abv=40`, `target_abv=40` → `spirit_needed` ≈ 1.111 (±0.001).
8. **`calculate` missing `input_spirit_abv`** — omit `input_spirit_abv` from POST body; request succeeds and defaults to 96.0.
9. **`calculate` uses POST target_abv over recipe default** — POST `target_abv=50` for a recipe with `target_abv_percentage=40`; response `target_abv_percentage` must equal `50.0`.

**Verify:**
```bash
python manage.py test
```
All tests must pass.

---

## Risks & Edge Cases

- `water_to_add` goes negative when `input_spirit_abv < target_abv`. The view must not crash — it returns the negative value. Cover this in tests only (test case 7 above approaches this scenario).
- The `0002` migration was never applied to `db.sqlite3`. Deleting and regenerating is safe. If anyone manually applied the old `0002`, they must run `python manage.py migrate calculator 0001` before applying the new one.
- `create_default_recipe` exits early if "Classic London Dry" already exists — existing rows get `target_abv_percentage=40.0` from the migration default automatically; the command only matters for fresh installs.
- `GinRecipe.save()` has custom single-default logic — must not be touched.
- Django model validators are only enforced on `full_clean()`, not `save()`. Tests must call `full_clean()` explicitly (Steps 2–4 in test list above).

---

## Validation Checklist

- [ ] `python manage.py check` passes after each step
- [ ] `python manage.py migrate` completes cleanly (Step 4)
- [ ] Django admin: `target_abv_percentage` appears in Recipe Details fieldset; values outside 10–99 are rejected
- [ ] `/calculate/` POST returns `spirit_needed`, `water_to_add`, `target_abv_percentage`, `input_spirit_abv`
- [ ] `/get-recipe/` POST returns `target_abv_percentage`
- [ ] UI: selecting a recipe pre-fills the Target Gin ABV field
- [ ] UI: Calculate with 1.5 L / 96% spirit / 40% target → ≈ 0.694 L spirit, ≈ 0.875 L water
- [ ] `python manage.py test` — all 9 tests pass
