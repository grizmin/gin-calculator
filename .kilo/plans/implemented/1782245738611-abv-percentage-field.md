# Plan: Add ABV Percentage Field to GinRecipe

## Goal
Add a user-facing `abv_percentage` (float, 5–90%) field to `GinRecipe`.  
Admins set it via the Django admin. The calculator frontend displays it alongside the existing `abv_volume` in the results panel.

> **Implementation rule:** Follow these steps exactly in order. Do not deviate, improvise, or make changes outside the listed files. If a step is ambiguous, stop and ask rather than guessing.

## Decisions
| Decision | Choice |
|---|---|
| Storage | New `FloatField` on `GinRecipe` — independent of `abv_volume` |
| Valid range | 5.0 – 90.0 (inclusive), enforced by Django validators |
| Migration default | `40.0` for all existing rows |
| API access | Read-only — returned by `get_recipe` and `calculate`; no user POST input |
| UI placement | Same `.abv-info` box in results + "Current Recipe Details" section |
| Admin | New field in `Recipe Details` fieldset |

## Files Affected (in order)

1. `calculator/models.py`
2. `calculator/migrations/0002_ginrecipe_abv_percentage.py` *(new)*
3. `calculator/admin.py`
4. `calculator/views.py`
5. `calculator/management/commands/create_default_recipe.py`
6. `calculator/templates/calculator/index.html`
7. `calculator/tests.py`

---

## Ordered Implementation Steps

### Step 1 — `calculator/models.py`
Add `abv_percentage` field to `GinRecipe`.

```python
from django.core.validators import MinValueValidator, MaxValueValidator

abv_percentage = models.FloatField(
    default=40.0,
    validators=[MinValueValidator(5.0), MaxValueValidator(90.0)],
    help_text="ABV percentage (5–90%)"
)
```

Place it after `abv_volume`.

**Verify:** `python manage.py check` passes with no errors.

---

### Step 2 — Migration `calculator/migrations/0002_ginrecipe_abv_percentage.py`
Run `python manage.py makemigrations` to auto-generate.  
Confirm the generated migration:
- Adds `abv_percentage` `FloatField` with `default=40.0`
- No data migration needed (default covers existing rows)

**Verify:** `python manage.py migrate --run-syncdb` (or `migrate`) completes without error.

---

### Step 3 — `calculator/admin.py`
Add `abv_percentage` to the `Recipe Details` fieldset:

```python
('Recipe Details', {
    'fields': ('base_volume', 'abv_volume', 'abv_percentage')
}),
```

Also add `abv_percentage` to `list_display`:

```python
list_display = ['name', 'base_volume', 'abv_volume', 'abv_percentage', 'is_active', 'is_default', 'created_by', 'created_at']
```

**Verify:** Django admin loads `/admin/calculator/ginrecipe/add/` and shows the `abv_percentage` field. Attempt to save with `4.0` → validation error. Save with `40.0` → success.

---

### Step 4 — `calculator/views.py`
**`get_recipe` view** — add `abv_percentage` to the recipe dict:

```python
'abv_percentage': recipe.abv_percentage,
```

**`calculate` view** — add `abv_percentage` to the response:

```python
'abv_percentage': recipe.abv_percentage,
```

No changes to parsing logic — `abv_percentage` is not a POST input.

**Verify:** POST to `/get-recipe/` with a valid recipe id returns JSON containing `"abv_percentage": 40.0`. POST to `/calculate/` returns `"abv_percentage": 40.0`.

---

### Step 5 — `calculator/management/commands/create_default_recipe.py`
In the `GinRecipe.objects.create(...)` call, add:

```python
abv_percentage=40.0,
```

**Verify:** Drop the existing "Classic London Dry" row (or run in a fresh DB), execute `python manage.py create_default_recipe`, query the row — `abv_percentage` is `40.0`.

---

### Step 6 — `calculator/templates/calculator/index.html`

**A. Results panel (`displayResults` JS function)**  
Extend the `.abv-info` div to display both values. Replace the static HTML:

```html
<div class="abv-info">
    <h4>Required ABV Volume</h4>
    <div id="abv-volume" class="abv-amount">0 L</div>
</div>
```

With:

```html
<div class="abv-info">
    <h4>ABV</h4>
    <div id="abv-percentage" class="abv-amount">0%</div>
    <div id="abv-volume" class="abv-amount" style="font-size:1.3rem; opacity:0.85;">0 L</div>
</div>
```

In `displayResults(data)`, add after the `abv_volume` line:

```js
document.getElementById('abv-percentage').textContent = `${data.abv_percentage}%`;
```

**B. Current Recipe Details panel (`displayCurrentRecipe` JS function)**  
In the template string inside `displayCurrentRecipe`, extend the `<p>` block:

```js
<strong>ABV:</strong> ${recipe.abv_percentage}%<br>
<strong>ABV Volume:</strong> ${recipe.abv_volume} liters
```

Remove or keep the old `ABV Volume` line as appropriate (keep both).

**Verify:** Load the page, select a recipe, click Calculate — the results panel shows `40%` above the litre figure. The "Current Recipe Details" section shows the ABV percentage.

---

### Step 7 — `calculator/tests.py`
Add tests covering:

1. **Model validation**: Creating a `GinRecipe` with `abv_percentage=4.0` raises `ValidationError`. Same for `91.0`. `40.0` succeeds.
2. **`get_recipe` API**: POST to `/get-recipe/` returns `abv_percentage` in the response JSON.
3. **`calculate` API**: POST to `/calculate/` returns `abv_percentage` in the response JSON.
4. **Default value**: A new recipe with no explicit `abv_percentage` defaults to `40.0`.

Each test class must create a `User` and a `GinRecipe` in `setUp`.

**Verify:** `python manage.py test` — all tests pass.

---

## Risks & Edge Cases
- `abv_volume=1.15` on `base_volume=1.0` in seed data implies 115% if derived — avoid deriving; `abv_percentage` is independent.
- `abv_percentage` validators run on `full_clean()` (called by admin forms and tests with `full_clean()`). Direct `save()` calls bypass them — this is standard Django behavior; document in tests.
- The committed `db.sqlite3` does NOT get the new column until `migrate` is run. CI or Docker that restores the committed DB must run `migrate` after pulling this change.

## Validation Checklist
- [ ] `python manage.py check` passes
- [ ] `python manage.py migrate` completes
- [ ] Django admin: `abv_percentage` field visible, out-of-range values rejected
- [ ] `/get-recipe/` JSON response includes `abv_percentage`
- [ ] `/calculate/` JSON response includes `abv_percentage`
- [ ] Frontend results panel shows `XX%` in the ABV box
- [ ] Frontend "Current Recipe Details" shows ABV percentage
- [ ] `python manage.py test` — all tests pass
