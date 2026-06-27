# Refactor A: Dead Code Removal + Admin Fields

Run after each step: `pyenv activate gin && python manage.py check && python manage.py test calculator && python -m pytest tests/`

---

## Step 1

**File:** `gin_calculator/settings.py`  
**Change:** Delete the line `BREWING_LOSS_PERCENTAGE = 10  # % volume lost during distillation` (line 133).  
**Verify:** `python manage.py check` — no errors.

---

## Step 2

**File:** `calculator/management/commands/delete_orphaned_recipes.py`  
**Change:** Delete the entire file.  
**Verify:** `python manage.py | grep delete_orphaned` — no output.

---

## Step 3

**File:** `calculator/management/commands/create_default_recipe.py`  
**Change:** Remove `import json` and `import os` from the top (these imports are unused).  
**Verify:** `python manage.py check` — no errors.

---

## Step 4

**File:** `calculator/admin.py`  
**Change:** In `GinRecipeAdmin.fieldsets`, add `'image_url'` to the `'Basic Information'` fieldset and add `'water_for_maceration'` to the `'Recipe Details'` fieldset.  
**Verify:** `python manage.py check` — no errors. Then open `http://localhost:8000/admin/calculator/ginrecipe/` and confirm both fields appear when editing a recipe.

---

## Step 5 — Full gate

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`  
All must pass before moving to Plan B.
