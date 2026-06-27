# Plan: Spirit Volume Calculator

> **Implementation rule:** Follow these steps exactly in order. Only modify files listed in the plan. Do not make unrequested improvements (UI, style, refactors). If a step contradicts the code, stop and report the conflict — do not resolve it by guessing. After each step, verify using the command listed before proceeding.

## Goal

Replace the broken `abv_percentage` field with a correct `target_abv_percentage` field on `GinRecipe`, and implement a spirit volume calculation that answers: "Given I want X litres of gin at Y% ABV using a spirit at Z% ABV, how much spirit do I need and how much water do I add?"

## Decisions

| Decision | Choice |
|---|---|
| Brewing loss | Global constant `BREWING_LOSS_PERCENTAGE = 10` in `settings.py` |
| Target ABV | Per-recipe `target_abv_percentage` field, default 40.0, validators 5–90%, overridable in UI |
| Input spirit ABV | UI-only input, default 96%, not stored |
| `abv_volume` field | Keep unchanged — it is the recipe's pure-alcohol ratio (litres per base litre) |
| Broken `0002` migration | Delete it; generate a clean replacement via `makemigrations` |

## Formula

```
scale_factor        = desired_volume / recipe.base_volume
pure_alcohol_needed = desired_volume × (target_abv / 100)
spirit_needed       = pure_alcohol_needed / (input_spirit_abv / 100) / (1 - BREWING_LOSS / 100)
water_to_add        = desired_volume - spirit_needed × (1 - BREWING_LOSS / 100)
```

Example — 1.5 L of gin at 40% using 96% spirit, 10% loss:
- pure_alcohol_needed = 1.5 × 0.40 = 0.60 L
- spirit_needed = 0.60 / 0.96 / 0.90 = 0.694 L
- water_to_add = 1.5 − 0.694 × 0.90 = 0.875 L

## Current State (what is broken)

- `calculator/migrations/0002_add_abv_percentage_field.py` — manually written, **never run**, wrong field definition (`null=True, blank=True`, no validators, no default). Must be deleted.
- `models.py` — has `abv_percentage` with correct validators but mismatched migration.
- `create_default_recipe.py` — seeds `abv_percentage=115.0` (wrong).
- `views.py` — returns `abv_percentage or 0` fallback (wrong).
- `index.html` — shows raw `abv_percentage` as a percentage display (wrong).

## Files Affected (in order)

1. `calculator/migrations/0002_add_abv_percentage_field.py` *(delete)*
2. `gin_calculator/settings.py`
3. `calculator/models.py`
4. `calculator/migrations/0002_ginrecipe_target_abv_percentage.py` *(generate via makemigrations)*
5. `calculator/admin.py`
6. `calculator/views.py`
7. `calculator/management/commands/create_default_recipe.py`
8. `calculator/templates/calculator/index.html`
9. `calculator/tests.py`

---

## Ordered Implementation Steps

### Step 1 — Delete broken migration

Delete `calculator/migrations/0002_add_abv_percentage_field.py`.

**Verify:** `ls calculator/migrations/` shows only `__init__.py` and `0001_initial.py`.

---

### Step 2 — `gin_calculator/settings.py`

Add at the bottom of the file, before the final blank line:

```python
# Brewing configuration
BREWING_LOSS_PERCENTAGE = 10  # % volume lost during distillation
```

**Verify:** `python manage.py check` passes.

---

### Step 3 — `calculator/models.py`

- Add import: `from django.conf import settings` (not needed in model itself — the constant is used in views, not here)
- Replace the existing `abv_percentage` field with `target_abv_percentage`:

```python
from django.core.validators import MinValueValidator, MaxValueValidator

target_abv_percentage = models.FloatField(
    default=40.0,
    validators=[MinValueValidator(5.0), MaxValueValidator(90.0)],
    help_text="Target ABV % of the finished gin (5–90%)"
)
```

Place it after `abv_volume`. Remove the `abv_percentage` field entirely. Do not touch `save()`.

**Verify:** `python manage.py check` passes with no errors.

---

### Step 4 — Generate migration

Run:

```bash
python manage.py makemigrations calculator --name ginrecipe_target_abv_percentage
```

Confirm the generated file:
- Adds `target_abv_percentage` as `FloatField(default=40.0, validators=[...])`
- No `null=True`
- Depends on `0001_initial`

Then run:

```bash
python manage.py migrate
```

**Verify:** `python manage.py migrate` completes with no errors.

---

### Step 5 — `calculator/admin.py`

Two changes only:

1. `list_display`: replace `'abv_volume'` entry with `'abv_volume', 'target_abv_percentage'`
2. `fieldsets` `'Recipe Details'` tuple: replace `'abv_volume'` with `'abv_volume', 'target_abv_percentage'`

Result:

```python
list_display = ['name', 'base_volume', 'abv_volume', 'target_abv_percentage', 'is_active', 'is_default', 'created_by', 'created_at']

('Recipe Details', {
    'fields': ('base_volume', 'abv_volume', 'target_abv_percentage')
}),
```

**Verify:** `python manage.py check` passes.

---

### Step 6 — `calculator/views.py`

**Imports to add at top:**

```python
from django.conf import settings
```

**`calculate` view** — replace the entire response-building block (after `scaled_abv_volume` is computed) with the new formula. Accept `input_spirit_abv` from POST body:

```python
from django.conf import settings

# inside calculate(), after scale_factor is computed:
input_spirit_abv = float(data.get('input_spirit_abv', 96.0))
brewing_loss = settings.BREWING_LOSS_PERCENTAGE / 100  # e.g. 0.10

pure_alcohol_needed = round(desired_volume * (recipe.target_abv_percentage / 100), 3)
spirit_needed = round(pure_alcohol_needed / (input_spirit_abv / 100) / (1 - brewing_loss), 3)
water_to_add = round(desired_volume - spirit_needed * (1 - brewing_loss), 3)

return JsonResponse({
    'success': True,
    'recipe_name': recipe.name,
    'recipe_description': recipe.description,
    'scaled_ingredients': scaled_ingredients,
    'target_abv_percentage': recipe.target_abv_percentage,
    'input_spirit_abv': input_spirit_abv,
    'spirit_needed': spirit_needed,
    'water_to_add': water_to_add,
    'scale_factor': round(scale_factor, 2),
})
```

Remove `scaled_abv_volume` and the `abv_volume` / `abv_percentage` keys from the response entirely.

**`get_recipe` view** — in the recipe dict, replace `'abv_volume': recipe.abv_volume` / `'abv_percentage': ...` with:

```python
'abv_volume': recipe.abv_volume,
'target_abv_percentage': recipe.target_abv_percentage,
```

Remove `abv_percentage or 0`.

**Verify:** `python manage.py check` passes.

---

### Step 7 — `calculator/management/commands/create_default_recipe.py`

In `GinRecipe.objects.create(...)`, replace `abv_percentage=115.0` with `target_abv_percentage=40.0`.

**Verify:** File saved, `python manage.py check` passes.

---

### Step 8 — `calculator/templates/calculator/index.html`

Four changes, each clearly scoped:

**A. Add `input_spirit_abv` input field** — inside `.input-section`, after the volume stepper `div.input-group` and before the calculate button:

```html
<div class="input-group">
    <label for="input_spirit_abv">Spirit ABV (%):</label>
    <input type="number" id="input_spirit_abv" value="96" min="5" max="96" step="1">
</div>
```

**B. Add `target_abv_percentage` override input** — in the same `.input-section`, after the spirit ABV input:

```html
<div class="input-group">
    <label for="target_abv">Target Gin ABV (%):</label>
    <input type="number" id="target_abv" value="40" min="5" max="90" step="0.5">
</div>
```

**C. Update the results `.abv-info` block** — replace:

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

1. In `calculateIngredients()`, add the two new inputs to the POST body:

```js
body: JSON.stringify({
    volume: volume,
    recipe_id: parseInt(recipeId),
    input_spirit_abv: parseFloat(document.getElementById('input_spirit_abv').value) || 96,
    target_abv: parseFloat(document.getElementById('target_abv').value) || 40,
})
```

2. In `displayResults(data)`, replace the ABV volume/percentage lines:

```js
document.getElementById('spirit-needed').textContent = `${data.spirit_needed} L`;
document.getElementById('result-spirit-abv').textContent = data.input_spirit_abv;
document.getElementById('water-to-add').textContent = data.water_to_add;
document.getElementById('result-target-abv').textContent = data.target_abv_percentage;
```

Remove references to `abv-volume`, `abv-percentage`.

3. In `displayCurrentRecipe(recipe)`, replace the `ABV Volume` line with:

```js
<strong>Target ABV:</strong> ${recipe.target_abv_percentage}%<br>
<strong>ABV Volume (base ratio):</strong> ${recipe.abv_volume} L
```

4. In `loadRecipeDetails()` success handler, after `currentRecipe = data.recipe`, populate the target ABV override field:

```js
document.getElementById('target_abv').value = data.recipe.target_abv_percentage;
```

**Verify:** Page loads, selecting a recipe populates the target ABV field. Clicking Calculate with 1.5 L, 96% spirit, 40% target returns spirit_needed ≈ 0.694 L and water_to_add ≈ 0.875 L.

---

### Step 9 — `calculator/tests.py`

Write tests from scratch. Each test class creates a `User` and `GinRecipe` in `setUp`.

Required test cases:

1. **Model default** — `GinRecipe` created without `target_abv_percentage` defaults to `40.0`.
2. **Model validation** — `target_abv_percentage=4.0` raises `ValidationError` on `full_clean()`. Same for `91.0`. `40.0` passes.
3. **`get_recipe` API** — POST to `/get-recipe/` returns `target_abv_percentage` in response JSON.
4. **`calculate` API — formula correctness** — POST with `volume=1.5`, `input_spirit_abv=96`, `target_abv=40` returns:
   - `spirit_needed` = 0.694 (±0.001)
   - `water_to_add` = 0.875 (±0.001)
5. **`calculate` API — different spirit ABV** — POST with `volume=1.0`, `input_spirit_abv=40`, `target_abv=40` returns `spirit_needed` = 1.111 (±0.001).
6. **`calculate` API — missing `input_spirit_abv`** — defaults to 96.0 without error.

**Verify:** `python manage.py test` — all tests pass.

---

## Risks & Edge Cases

- `water_to_add` can go negative if `input_spirit_abv` is lower than `target_abv_percentage`. The view should not crash — it will just return a negative number. Document this in the test but do not add UI validation in this plan.
- The `0002` migration was never applied to `db.sqlite3` (pyenv could not activate during the prior session). Deleting and regenerating it is safe. Anyone who somehow did run `0002` manually will need to roll back with `python manage.py migrate calculator 0001` before applying the new `0002`.
- `create_default_recipe` exits early if "Classic London Dry" already exists. Existing rows will get `target_abv_percentage=40.0` from the migration default automatically.

## Validation Checklist

- [ ] `python manage.py check` passes after each step
- [ ] `python manage.py migrate` completes cleanly
- [ ] Django admin shows `target_abv_percentage` field in Recipe Details; out-of-range values rejected
- [ ] `/calculate/` POST returns `spirit_needed`, `water_to_add`, `target_abv_percentage`
- [ ] `/get-recipe/` POST returns `target_abv_percentage`
- [ ] Frontend: selecting a recipe populates the Target Gin ABV field
- [ ] Frontend: Calculate with 1.5 L / 96% / 40% shows ≈ 0.694 L spirit, ≈ 0.875 L water
- [ ] `python manage.py test` — all tests pass
