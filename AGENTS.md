# AGENTS.md

## Project
Gin Ingredients Calculator — a Django web app that scales gin recipe
ingredients to a desired volume, with an admin interface for managing recipes.

- Framework: Django >= 4.2 (Python)
- Database: SQLite (`db.sqlite3` is committed on purpose — it holds sample
  data used by/for tests; do not delete or regenerate it casually)
- Django project package: `gin_calculator`
- App: `calculator`

## Environment
Python env is managed with **pyenv**. Always activate first:

```bash
pyenv activate gin
```

Do NOT create a new `venv/` (the README's manual-setup venv steps are outdated).

## Common commands
Run all from the repo root after `pyenv activate gin`:

- Run dev server: `python manage.py runserver`
- Run unit tests: `python manage.py test calculator`
  (must be scoped to `calculator` — a bare `manage.py test` also tries to
  import the Playwright suite below and errors)
- Run UI tests: `python -m pytest tests/` (needs `playwright install chromium`
  once; spins up its own dev server against the committed `db.sqlite3`)
- Apply migrations: `python manage.py migrate`
- Make migrations: `python manage.py makemigrations`
- Seed default recipe: `python manage.py create_default_recipe`

Docker (alternative): `docker-compose up` → app on http://localhost:8000,
admin at /admin (admin/admin123).

## Architecture
- `calculator/models.py`
  - `GinRecipe`: name, base_volume, abv_volume, is_active, is_default,
    target_abv_percentage, image_url, created_by (User FK). `save()`
    enforces a single default recipe.
  - `RecipeIngredient`: recipe FK (`related_name='ingredients'`), name,
    amount (g per base volume), is_optional, notes, order.
    `unique_together = ['recipe', 'name']`.
- `calculator/views.py` — server-rendered `index` plus two JSON POST endpoints:
  - `calculate`: scales ingredients by `desired_volume / base_volume`.
  - `get_recipe`: returns recipe details.
  - Note: both JSON endpoints are `@csrf_exempt`.
- `calculator/management/commands/create_default_recipe.py` — seeds the
  "Classic London Dry" recipe.
- `create_custom_default_recipe.py`, `create_famous_recipes.py` — additional
  recipe-seeding commands (the latter has a known fixture-path bug under
  investigation).
- Templates: `calculator/templates/calculator/index.html` (AJAX frontend).

## Conventions
- Keep scaling math in views consistent (amounts rounded to 2 decimals).
- When adding ingredients programmatically, respect `unique_together` and `order`.
- Update/add tests in `calculator/tests.py` and run `python manage.py test`
  before finishing changes.

## Plan Execution
When given a plan file to implement:
- Follow steps in the listed order, one at a time
- Only modify files listed in the plan
- Do not make unrequested improvements (UI, style, refactors)
- If a step contradicts the code, stop and report the conflict — do not resolve it by guessing
- After each step, verify using the command listed in the plan before proceeding

## Code Review
All pull requests must pass:
- `python manage.py check` 
- `python manage.py test calculator`
- `python -m pytest tests/`
- No linting errors (no linter is currently configured — this gate is a
  no-op until one is added)

## Commit Style
Use conventional commits:
- feat: Add new functionality
- fix: Correct a bug  
- docs: Update documentation
- style: Formatting changes (no logic changes)
- refactor: Cleanup without changing behavior
- test: Add/remove tests
