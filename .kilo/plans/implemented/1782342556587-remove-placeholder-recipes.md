# Remove Unused Placeholder Recipes

**Goal:** Delete three unused placeholder recipes from `db.sqlite3`:
- `High ABV Recipe` (id 3)
- `Low ABV Recipe` (id 4)
- `Medium ABV Recipe` (id 5)

These are not referenced in any code, fixture, or seed command. They each have 1 ingredient and identical 40% ABV — clearly leftover placeholders.

## Steps

1. **Delete recipes from database** — run Django shell command to delete ids 3, 4, 5 (ingredients cascade-delete via FK):
   ```
   DJANGO_SETTINGS_MODULE=gin_calculator.settings python -c "
   import django; django.setup()
   from calculator.models import GinRecipe
   deleted, info = GinRecipe.objects.filter(id__in=[3,4,5]).delete()
   print(f'Deleted {deleted} objects')
   "
   ```
   Verify: `DJANGO_SETTINGS_MODULE=gin_calculator.settings python -c "import django; django.setup(); from calculator.models import GinRecipe; [print(r.id, r.name) for r in GinRecipe.objects.all()]"` — ids 3/4/5 no longer listed.

2. **Run tests** — `python manage.py test calculator` — all 8 tests pass.

3. **Confirm UI** — load page, verify dropdown no longer shows the three recipes.
