# Refactor C: Fixture Image URLs + Path Fix

Prerequisite: Plan B complete and green.

Run after each step: `pyenv activate gin && python manage.py check && python manage.py test calculator && python -m pytest tests/`

---

## Context

`create_famous_recipes.py` hardcodes 8 image URLs in an `IMAGE_URLS` dict and constructs the fixture path with a fragile 4-level `os.path.dirname()` chain. AGENTS.md notes "a known fixture-path bug under investigation."

---

## Step 1

**File:** `calculator/fixtures/famous_gin_recipes.json`  
**Change:** For each of the 8 recipe objects in the JSON, add an `"image_url"` key using the URL currently found in the `IMAGE_URLS` dict at the top of `create_famous_recipes.py`. Insert `"image_url"` between `"name"` and `"description"` for each recipe. Do not change any other fields.  
**Verify:** `python -c "import json; data=json.load(open('calculator/fixtures/famous_gin_recipes.json')); assert all('image_url' in r for r in data), 'Missing image_url'"` — no assertion error.

---

## Step 2

**File:** `calculator/management/commands/create_famous_recipes.py`  
**Change:**
- Remove the `IMAGE_URLS` dict (lines 20–29 approx).
- Replace the `os.path.dirname()` fixture path construction with:
  ```python
  from pathlib import Path
  fixture_path = Path(__file__).resolve().parent.parent.parent.parent / 'calculator' / 'fixtures' / 'famous_gin_recipes.json'
  ```
- Remove the image-URL backfill block (the loop that sets `recipe.image_url` from `IMAGE_URLS` after creation).
- Update recipe creation to use `recipe_data.get('image_url', '')` when setting `image_url` on the recipe object.  
**Verify:** `python manage.py create_famous_recipes` — prints success or "already exists" for all 8 recipes. No FileNotFoundError.

---

## Step 3 — Full gate

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`  
All must pass before moving to Plan D.
