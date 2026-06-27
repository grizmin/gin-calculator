# Famous Gin Recipes Seed Plan

## Status (as of last review)
The skeleton already exists and is committed to the working tree:
- `calculator/fixtures/famous_gin_recipes.json` — exists, all 8 recipes, correct
  ingredient amounts/`is_optional`/`±X%` variation notes.
- `calculator/management/commands/create_famous_recipes.py` — exists, runs, idempotent.
- `calculator/tests.py::FamousRecipesCommandTest` — exists with 5 of 7 planned tests; all pass.
- All 8 recipes are already loaded into the committed `db.sqlite3`.

**What's NOT done yet (the actual remaining work):**
- The `description` field for all 8 recipes is still a generic one-liner
  ("A classic London Dry gin with juniper, coriander...") instead of the
  distilling-process narrative drafted in the Recipe Data section below.
- The command only backfills `image_url` on already-existing recipes — it does
  **not** backfill `description` or ingredient `notes`, so editing the fixture
  alone will not update the already-seeded rows in `db.sqlite3`.
- Two tests (`test_recipes_have_description_notes`, `test_ingredients_have_variation_notes`)
  are missing from `tests.py`.

This plan's remaining steps (see "Files to Update" below) are scoped to close
exactly these three gaps — do not recreate the fixture or command from scratch.

## Goal
Fill in the researched distilling-process descriptions for the 8 already-seeded
famous gin recipes, make the enrichment actually propagate into the database
(not just the fixture file), and lock it in with tests.

## Context
- Framework: Django, app `calculator`
- Existing pattern: `calculator/management/commands/create_default_recipe.py` — idempotent command that creates one recipe and its ingredients
- Models:
  - `GinRecipe` (name, description, image_url, base_volume, abv_volume, target_abv_percentage, is_active, is_default, created_by FK)
  - `Ingredient` (name, unique) — shared lookup table
  - `RecipeIngredient` (recipe FK, ingredient FK, amount, is_optional, notes, order) — links recipe to ingredient
- No model changes required — famous recipes are plain `GinRecipe` objects

## Decisions
| Decision | Choice |
|---|---|
| Recipes to seed | All 8: Tanqueray, Hendrick's, Bombay Sapphire, Beefeater, Aviation, Gordon's, Monkey 47, Sipsmith |
| Data storage | `calculator/fixtures/famous_gin_recipes.json` — canonical data source |
| Delivery | Management command `create_famous_recipes` |
| `abv_volume` | `base_volume * (target_abv_percentage / 100)` |
| Ingredient amounts | Midpoint of researched range, rounded to 1 decimal |
| Ingredient notes | Variation note e.g. `"±20% typical variation"` |
| Recipe `description` | Brewing/distilling process notes for each brand |
| `Ingredient` model | Use `get_or_create` for each botanical name before linking |
| `is_default` | `False` for all seeded recipes |
| Idempotency | Skip recipe by name if it already exists, but backfill `image_url`, `description`, and ingredient `notes` if they differ from the fixture (already implemented for `image_url`; `description`/`notes` backfill is the new work) |

## Recipe Data (source of truth for the JSON file)

### 1. Tanqueray London Dry
- **Description**: "Tanqueray is distilled in traditional copper pot stills using a simple single-shot method. Only 4 botanicals are used — the fewest among major London Dry gins — making it deliberately juniper-forward. The spirit is 96% ABV neutral grain spirit, with botanicals macerated then distilled in one continuous process. No additives or sugar are permitted after distillation."
- base_volume: 1.0, target_abv: 47.3%, abv_volume: 0.473
- Botanicals: Juniper berries 17.5g, Coriander seeds 5.0g, Angelica root 2.5g, Liquorice root 1.5g
- All ingredient notes: "±15% typical variation" (Angelica/Liquorice ±20%)

### 2. Hendrick's
- **Description**: "Hendrick's is distilled in two separate stills: first a Carter-Head still for the base botanicals, then a Bennett pot still for the floral botanicals. After distillation, cucumber and rose essences are added post-distillation (not vapour-infused), giving its signature profile. The gin is bottled at 44% ABV. The two-still process separates the heavier botanicals from the delicate florals."
- base_volume: 1.0, target_abv: 44.0%, abv_volume: 0.44
- Botanicals: Juniper berries 12.0g, Coriander seeds 6.5g, Angelica root 3.0g, Orris root 2.5g, Elderflower 2.5g, Chamomile 1.5g, Cubeb pepper 1.5g, Orange peel 2.5g, Lemon peel 1.5g, Caraway seeds 1.5g, Yarrow 0.75g
- Post-distillation essences (is_optional=True): Rose essence 0.0g, Cucumber essence 0.0g
- Ingredient notes: "±15% typical variation" (Yarrow ±30%; Rose/Cucumber essences: "added post-distillation, amount varies by batch")

### 3. Bombay Sapphire
- **Description**: "Bombay Sapphire uses the Carter-Head vapour infusion process exclusively — botanicals are placed in a basket above the spirit (never touching the liquid), and vapour passes through them. This produces a lighter, more delicate gin compared to maceration methods. The base is 96.3% ABV wheat neutral spirit. All 10 botanicals are printed on the bottle. No sugar or additives after distillation."
- base_volume: 1.0, target_abv: 47.0%, abv_volume: 0.47
- Botanicals: Juniper berries 12.5g, Coriander seeds 6.5g, Angelica root 3.0g, Orris root 2.0g, Lemon peel 3.0g, Cassia bark 1.5g, Cubeb pepper 1.5g, Grains of paradise 1.5g, Almonds 3.0g, Liquorice root 1.5g
- All ingredient notes: "±15% typical variation" (Orris/Cassia/Cubeb/Grains of paradise/Almonds/Liquorice ±20%)

### 4. Beefeater London Dry
- **Description**: "Beefeater follows the original 1895 recipe with a 24-hour maceration process — all 9 botanicals are steeped in 96% ABV grain spirit for a full day before distillation in a traditional copper pot still. This extended maceration extracts maximum flavour from the botanicals, particularly the Seville orange peel. The recipe has remained unchanged since its creation."
- base_volume: 1.0, target_abv: 40.0%, abv_volume: 0.40
- Botanicals: Juniper berries 16.0g, Coriander seeds 7.0g, Angelica root 4.0g, Angelica seeds 1.5g, Orris root 2.5g, Seville orange peel 4.0g, Lemon peel 3.0g, Liquorice root 1.5g, Almonds 1.5g
- All ingredient notes: "±15% typical variation" (Angelica root/seeds/Orris/Seville orange/Liquorice/Almonds ±20%)

### 5. Aviation American Gin
- **Description**: "Aviation is a 'New Western' gin that deliberately de-emphasizes juniper in favour of floral and herbal botanicals. Produced at House Spirits Distillery in Portland, Oregon. Botanicals are steeped for 18 hours then re-distilled in a 400-gallon copper pot still. The lavender and Indian sarsaparilla give it a distinctive floral, earthy profile. Named after the Aviation cocktail."
- base_volume: 1.0, target_abv: 42.0%, abv_volume: 0.42
- Botanicals: Juniper berries 8.0g, Coriander seeds 5.0g, Cardamom 3.0g, Sweet orange peel 2.5g, Bitter orange peel 1.5g, Lavender 2.5g, Indian sarsaparilla 2.5g, Anise seed 1.5g
- All ingredient notes: "±20% typical variation"

### 6. Gordon's London Dry
- **Description**: "Gordon's is one of the oldest gin brands (established 1769), with a recipe that has remained largely unchanged. It uses a traditional London Dry process with maceration followed by distillation in copper pot stills. Notably produces a 'dry' gin with no added sugar. The 7-botanical bill is a classic, minimal profile. Bottled at 37.5% ABV in the UK (40% in the US)."
- base_volume: 1.0, target_abv: 37.5%, abv_volume: 0.375
- Botanicals: Juniper berries 16.0g, Coriander seeds 6.5g, Angelica root 3.0g, Liquorice root 1.5g, Orris root 1.5g, Orange peel 2.5g, Lemon peel 1.5g
- All ingredient notes: "±15% typical variation" (Angelica/Liquorice/Orris/Orange/Lemon ±20%)

### 7. Monkey 47 Schwarzwald Dry Gin
- **Description**: "Monkey 47 is produced in the Black Forest (Schwarzwald), Germany, using a molasses-based neutral spirit rather than grain. The gin features 47 botanicals — the most of any major gin brand. Lingonberries are macerated for approximately one week as the 'base note', while the remaining 46 botanicals are added 36 hours before distillation. Distilled in a 1920s-era copper still. Bottled at 47% ABV. The botanicals include herbs, flowers, spices, and forest berries sourced from the Black Forest region."
- base_volume: 1.0, target_abv: 47.0%, abv_volume: 0.47
- Botanicals (47 total): Juniper berries 10.0g, Lingonberries 12.5g, Coriander seeds 4.0g, Angelica root 2.5g, Orris root 1.5g, Cassia bark 1.5g, Cardamom 1.5g, Lemon peel 1.5g, Pomelo peel 1.5g, Black pepper 1.5g, Cubeb pepper 0.75g, Grains of paradise 0.75g, Lavender 1.5g, Chamomile 1.5g, Elderflower 1.5g, Rose mallow 0.75g, Dog rose hips 0.75g, Honeysuckle 0.75g, Jasmine 0.75g, Spruce shoots 1.5g, Sloe berries 1.5g, Hawthorn berries 0.75g, Blackberry leaves 0.75g, Cranberry 1.5g, Lemon balm 0.75g, Lemon verbena 0.75g, Lemongrass 0.75g, Makrut lime leaves 0.75g, Sage 0.75g, Sweet flag (calamus) 0.75g, Bee balm 0.75g, Yarrow 0.75g, Marshmallow root 0.75g, Ginger 1.5g, Nutmeg 0.75g, Cloves 0.4g, Cinnamon 0.75g, Ambrette seed 0.4g, Acacia flowers 0.4g, Liquorice root 1.5g, Almonds 0.75g, Pimento 0.75g, Rose hip 0.75g, Orange peel 0.75g, Vanilla 0.4g
  - NOTE: The original research lists 47 items but some are duplicates (Chamomile/Camomile, Almonds/Almond). Deduplicate to exactly 47 unique entries.
- All ingredient notes: "±25% typical variation (Monkey 47 botanical bill)"

### 8. Sipsmith London Dry
- **Description**: "Sipsmith was the first London distillery to operate legally in 150 years (opened 2009). Uses a single-shot distillation method in their copper pot still named 'Prudence'. The base is 100% wheat neutral spirit. All 10 botanicals are added in a single batch and distilled together. The gin is bottled at 41.6% ABV — an unusual strength chosen to balance flavour extraction. No additives or sugar after distillation."
- base_volume: 1.0, target_abv: 41.6%, abv_volume: 0.416
- Botanicals: Juniper berries 15.0g, Coriander seeds 7.0g, Angelica root 3.5g, Orris root 2.5g, Lemon peel 3.0g, Orange peel (bitter) 2.5g, Cassia bark 1.5g, Cinnamon 0.75g, Liquorice root 1.5g, Almonds 1.5g
- All ingredient notes: "±15% typical variation" (Angelica/Orris/Cassia/Cinnamon/Liquorice/Almonds ±20%)

## Files to Update

These are edits to **existing** files — do not regenerate them from scratch.
Preserve all existing logic (e.g. the `IMAGE_URLS` dict and image backfill
branch in the command) that isn't called out below.

### Step 1 — Update recipe descriptions in the fixture
**File**: `calculator/fixtures/famous_gin_recipes.json`

For each of the 8 recipe objects, replace the `description` value with the
distilling-process narrative already drafted in the "Recipe Data" section
above (lines 32, 38, 45, 51, 57, 63, 69, 76 of this plan). Do not change any
other field — `base_volume`, `abv_volume`, `target_abv_percentage`,
`ingredients` (amounts/notes/is_optional) are already correct.

**Verify**:
```bash
python -c "
import json
data = json.load(open('calculator/fixtures/famous_gin_recipes.json'))
for r in data:
    assert len(r['description']) > 100, r['name'] + ' description too short'
print('all 8 descriptions updated')
"
```

---

### Step 2 — Make the command backfill description + notes on existing recipes
**File**: `calculator/management/commands/create_famous_recipes.py`

The `if existing:` branch currently only backfills `image_url`. Extend it to
also backfill `description` when it differs from the fixture, and backfill
each `RecipeIngredient.notes` when it differs. This is required because
`db.sqlite3` already has all 8 recipes loaded — without this change, Step 1's
JSON edits will never reach the database.

Add inside the existing `if existing:` block (after the `image_url` check),
before `continue`:
```python
if existing.description != recipe_data['description']:
    existing.description = recipe_data['description']
    existing.save(update_fields=['description'])

for ing_data in recipe_data['ingredients']:
    ri = existing.ingredients.filter(ingredient__name=ing_data['name']).first()
    if ri and ri.notes != ing_data['notes']:
        ri.notes = ing_data['notes']
        ri.save(update_fields=['notes'])
```

**Verify**:
```bash
pyenv activate gin
python manage.py create_famous_recipes
python manage.py shell -c "
from calculator.models import GinRecipe
print(GinRecipe.objects.get(name='Tanqueray London Dry').description)
"
```
Should print the new distilling-process description, not the old one-liner.

---

### Step 3 — Add the two missing tests
**File**: `calculator/tests.py` (append to existing `FamousRecipesCommandTest`, do not touch other tests)

Add:
- `test_recipes_have_description_notes`: call command, assert every one of the
  8 seeded recipes has a `description` longer than 100 chars (i.e. not the old
  one-liner placeholder).
- `test_ingredients_have_variation_notes`: call command, assert every seeded
  `RecipeIngredient.notes` is non-blank and contains `"±"`.
- `test_description_backfill_updates_existing`: create a recipe matching one
  fixture entry by name with a stale `description`, run the command, assert
  the `description` was overwritten to match the fixture (covers Step 2).

**Verify**: `pyenv activate gin && python manage.py test calculator.tests.FamousRecipesCommandTest` — all 8 tests pass.

---

## Risks
- **Already-seeded `db.sqlite3` won't pick up fixture changes without Step 2.**
  This is the main risk for this round of work — Step 1 alone (editing the
  JSON) is silently inert against the committed database, since the command
  currently skips fully on existing recipes except for `image_url`. Steps 1
  and 2 must ship together.
- Monkey 47 has 47 botanicals already deduplicated in the fixture (verified:
  47 unique ingredient names) — no further action needed here.
- `unique_together` on `RecipeIngredient` is `['recipe', 'ingredient']` (FK),
  not `['recipe', 'name']` — functionally equivalent since `Ingredient.name`
  is itself unique, but don't write code assuming a `name` field on the
  through-model.
- The command requires a superuser to assign `created_by`. The test class's
  `setUp` already creates one.

## Validation
```bash
pyenv activate gin
python manage.py check                                       # no errors
python manage.py create_famous_recipes                       # backfills description/notes on existing recipes
python manage.py shell -c "from calculator.models import GinRecipe; print(GinRecipe.objects.get(name='Tanqueray London Dry').description)"
                                                               # should show new distilling-process text, not old one-liner
python manage.py test calculator.tests.FamousRecipesCommandTest  # all 8 tests pass (5 existing + 3 new)
python manage.py test calculator                              # full suite still green
python -m pytest tests/                                       # UI suite still green
```
