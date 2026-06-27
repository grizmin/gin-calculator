# Refactor B: Shared Ingredient-Creation Helpers

Prerequisite: Plan A complete and green.

Run after each step: `pyenv activate gin && python manage.py check && python manage.py test calculator && python -m pytest tests/`

---

## Context

Four files duplicate an identical ingredient-creation loop and a superuser-lookup pattern:
- `calculator/management/commands/create_default_recipe.py`
- `calculator/management/commands/create_custom_default_recipe.py`
- `calculator/management/commands/create_famous_recipes.py`
- `docker-setup.py`

---

## Step 1

**File:** `calculator/management/commands/_helpers.py` (NEW)  
**Change:** Create this file with two functions:

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

**Verify:** `python manage.py check` — no errors.

---

## Step 2

**File:** `calculator/management/commands/create_default_recipe.py`  
**Change:**
- Remove `from django.contrib.auth.models import User` and `from calculator.models import Ingredient, RecipeIngredient` imports.
- Add `from calculator.management.commands._helpers import get_superuser, create_recipe_ingredients`.
- Replace the manual `admin_user = User.objects.filter(is_superuser=True).first()` lookup with `admin_user = get_superuser(self)`.
- Replace the manual ingredient for-loop with `create_recipe_ingredients(recipe, ingredients_data)`.  
**Verify:** `python manage.py create_default_recipe` — prints "already exists" or creates successfully. Then run `python manage.py check && python manage.py test calculator`.

---

## Step 3

**File:** `calculator/management/commands/create_custom_default_recipe.py`  
**Change:**
- Same import swap as Step 2.
- Replace manual superuser lookup with `get_superuser(self)`.
- Replace manual ingredient loop with `create_recipe_ingredients(recipe, ingredients_data)`.  
**Verify:** `python manage.py create_custom_default_recipe --name "TestB" --abv-percentage 45` — creates recipe. Then `python manage.py check && python manage.py test calculator`.

---

## Step 4

**File:** `calculator/management/commands/create_famous_recipes.py`  
**Change:**
- Same import swap as Step 2.
- Replace manual superuser lookup with `get_superuser(self)`.
- Replace manual ingredient loop with `create_recipe_ingredients(recipe, ingredients_data)`.  
**Verify:** `python manage.py create_famous_recipes` — prints success or "already exists" for all recipes. Then `python manage.py check && python manage.py test calculator`.

---

## Step 5

**File:** `docker-setup.py`  
**Change:**
- Add `from calculator.management.commands._helpers import create_recipe_ingredients` (full import path, not relative).
- Replace the manual ingredient for-loop with `create_recipe_ingredients(recipe, ingredients_data)`.  
**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`

---

## Step 6 — Full gate

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`  
All must pass before moving to Plan C.
