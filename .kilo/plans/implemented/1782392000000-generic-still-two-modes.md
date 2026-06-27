# Generic Still Calculator — Two Modes (Compound + Distill) with Native Rebrand

## Goal
Turn the gin-only app into a generic spirit calculator with **two modes** sharing one
final proofing step:
- **Compound mode** — existing flow: neutral spirit + botanicals + maceration + still
  yield → scaled recipe (gin, aquavit, absinthe…). Recipe-driven (DB).
- **Distill mode** — new flow for fermented washes (rakia, fruit brandy). Free-form
  (no DB recipe in v1): wash volume + wash ABV + still capacity + collection ABV →
  pure alcohol, expected distillate, batch count, cut guidance, proofing water.

Rebrand from "Gin" to "Spirit" is **built in** — the model is renamed `GinRecipe → Recipe`
and all user-facing "Gin" strings become generic.

## Scope decisions (resolved with user)
| Decision | Choice |
|---|---|
| Equipment target | Vevor countertop still (boiler + condenser, no reflux) |
| Compound mode | Recipe-driven, reuses existing calc; add `category` field |
| Distill mode | Free-form calculator, **no DB recipe** in v1 |
| Shared step | Final proofing (dilute pure alcohol to target ABV) |
| Model rename | `GinRecipe → Recipe` via explicit RenameModel migration (no interactive prompt) |
| Project dir | `gin_calculator/` stays as-is — NOT renamed (high breakage, zero user value) |
| Whiskey/rum aging | Out of scope (no aging, no fermentation in-app) |

## Worked example (sanity check — matches user's real run)
3 kg ≈ 3 L wash @ ~10% ABV → `pure_alcohol = 3 × 0.10 = 0.30 L`.
Collected @ 43% → `distillate = 0.30 / 0.43 ≈ 0.70 L` ✅ (user got ~700 g rakia).

> **Executor note:** Do ONE step at a time, run its Verify, then continue. Each step lists
> exactly which file(s) to touch. The **TL;DR** line states the single thing the step must achieve.

---

## PHASE A — Native rebrand (model + strings)

### Step A1 — Rename model class
**TL;DR:** In one file, change the class name `GinRecipe` to `Recipe` and the 3 places that reference it.
**File:** `calculator/models.py`
**Change:** Rename `class GinRecipe(models.Model)` → `class Recipe(models.Model)`. Inside its
`save()`, change `GinRecipe.objects.filter(...)` → `Recipe.objects.filter(...)`. Update the
`RecipeIngredient.recipe` FK from `ForeignKey(GinRecipe, ...)` → `ForeignKey(Recipe, ...)`.
Update `target_abv_percentage` help_text "finished gin" → "finished spirit".
**Verify:** `python manage.py makemigrations --dry-run --check` shows a model rename is pending (do NOT generate yet — Step A2 writes it explicitly).

### Step A2 — Explicit rename migration (avoids interactive prompt)
**TL;DR:** Create one new migration file that renames the DB table from GinRecipe to Recipe.
**File:** `calculator/migrations/0008_rename_ginrecipe_recipe.py` (new)
**Change:** Hand-write:
```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('calculator', '0007_ginrecipe_water_for_maceration')]
    operations = [migrations.RenameModel('GinRecipe', 'Recipe')]
```
**Verify:** `python manage.py migrate` runs clean; `python manage.py makemigrations --check` reports no remaining changes.

### Step A3 — Update Python references
**TL;DR:** Find-and-replace `GinRecipe` with `Recipe` in every non-migration .py file.
**Files:** `calculator/views.py`, `calculator/admin.py`,
`calculator/management/commands/{create_famous_recipes,create_default_recipe,create_custom_default_recipe,delete_orphaned_recipes}.py`,
`tests/test_calculator_views.py`
**Change:** Replace every `GinRecipe` with `Recipe` (imports + usages). No logic changes.
**Verify:** `grep -rn "GinRecipe" calculator/ tests/ | grep -v migrations/000` returns nothing; `python manage.py test` collects without ImportError.

### Step A4 — Rebrand user-facing strings
**TL;DR:** Swap the visible "Gin" words in the template for generic "Spirit" wording.
**File:** `calculator/templates/calculator/index.html`
**Change:**
- `<title>Gin Calculator` → `<title>Spirit Calculator`
- `<h1>Gin Calculator</h1>` → `<h1>Spirit Calculator</h1>`
- footer `Gin Calculator &mdash; scale any recipe…` → `Spirit Calculator &mdash; scale any recipe…`
- `Target gin ABV` → `Target ABV`
- Leave `Botanicals` heading (still correct for compound mode; distill mode hides it).
**Verify:** Page renders; no "Gin" visible in compound UI except recipe names.

---

## PHASE B — Mode switcher shell

### Step B1 — Add `category` to Recipe (compound grouping)
**TL;DR:** Add one new text field `category` to the Recipe model and make its migration.
**Files:** `calculator/models.py` + new migration `0009_recipe_category.py`
**Change:** Add `category = models.CharField(max_length=20, default='gin', choices=[('gin','Gin'),('aquavit','Aquavit'),('absinthe','Absinthe'),('other','Other')])`.
Generate the migration with `python manage.py makemigrations calculator` (non-interactive — it's an additive field with default).
**Verify:** `python manage.py migrate`; admin shows the new dropdown.

### Step B2 — Mode toggle markup
**TL;DR:** Add two toggle buttons and wrap existing content in a panel + an empty second panel.
**File:** `calculator/templates/calculator/index.html`
**Change:** Above `.main-content` (or at top of the right column), add a segmented control:
```html
<div class="mode-toggle" role="tablist">
  <button id="mode-compound" class="mode-btn active" type="button">Compound · gin / aquavit</button>
  <button id="mode-distill" class="mode-btn" type="button">Distill · rakia / brandy</button>
</div>
```
Wrap the existing recipe+params+results markup in `<div id="compound-panel">`. Add an empty
`<div id="distill-panel" hidden></div>` (filled in Phase C).
**Verify:** Two buttons render; compound panel visible by default; distill panel hidden.

### Step B3 — Mode toggle CSS
**TL;DR:** Add styles for the toggle buttons, matching the existing card/spirit-option look.
**File:** `calculator/static/calculator/calculator.css`
**Change:** Append `.mode-toggle` (flex, gap) and `.mode-btn` / `.mode-btn.active` styles
reusing existing tokens (`--color-accent`, `--color-surface-2`, `--radius-md`). Match the
`.spirit-option` visual language already present.
**Verify:** Buttons styled; active state highlights in accent color.

### Step B4 — Mode toggle JS
**TL;DR:** Write the JS that shows the chosen panel, hides the other, and recalculates.
**File:** `calculator/templates/calculator/index.html` (`<script>`)
**Change:** Add a `setMode(mode)` that toggles `.active` on the two buttons and `hidden` on
the two panels, persists choice in `localStorage('calc_mode')`, and calls the active mode's
calculate fn (`calculateLocally` for compound, `calculateDistill` for distill). Wire both
buttons' `click`. On load, restore saved mode (default compound).
**Verify:** Clicking toggles panels and recalculates; reload preserves last mode.

---

## PHASE C — Distill mode (rakia / fruit brandy)

### Step C1 — Distill panel markup
**TL;DR:** Inside the empty distill panel, add 5 number inputs and 4 result boxes.
**File:** `calculator/templates/calculator/index.html` (inside `#distill-panel`)
**Change:** Add a params card + results card mirroring compound styling:
- Inputs (`.params-input`): `wash_volume` (L, default 3), `wash_abv` (%, default 10),
  `still_capacity` (L, default 3), `collection_abv` (%, default 43), `distill_target_abv`
  (%, default 45).
- Result stats (`.volume-stat`): `#d-pure-alcohol` (Pure alcohol, L), `#d-distillate`
  (Expected distillate, L), `#d-batches` (Batches), `#d-proof-water` (Water to bottle, L),
  plus a `.volume-stat-note` for cut guidance text `#d-cuts`.
**Verify:** Five inputs + four stats render when Distill mode active; placeholders show `—`.

### Step C2 — Distill calculation JS
**TL;DR:** Write `calculateDistill()` that reads the 5 inputs and fills the 4 result boxes.
**File:** `calculator/templates/calculator/index.html` (`<script>`)
**Change:** Add `calculateDistill()`:
```js
const washVol = parseFloat(v('wash_volume'));
const washAbv = parseFloat(v('wash_abv'));
const cap     = parseFloat(v('still_capacity'));
const collAbv = parseFloat(v('collection_abv'));
const tgtAbv  = parseFloat(v('distill_target_abv'));
// guards: all > 0; collAbv > tgtAbv; washAbv < collAbv  → else show warning placeholder
const pureAlcohol = round2(washVol * washAbv / 100);
const distillate  = round2(pureAlcohol / (collAbv / 100));
const batches     = Math.ceil(washVol / cap);
const finalVol    = round2(pureAlcohol / (tgtAbv / 100));
const proofWater  = round2(finalVol - distillate);
const cutsNote    = 'Discard first ~' + Math.max(20, Math.round(pureAlcohol*1000*0.05))
                  + ' ml as heads; stop collecting (tails) when stream drops below ~20% ABV.';
```
Render into the `#d-*` spans. `round2(x)=Math.round(x*100)/100`; `v(id)=document.getElementById(id).value`.
**Verify (console, Distill mode):** wash 3 / abv 10 / coll 43 → `pure_alcohol=0.3`, `distillate≈0.7`, `batches=1`. Matches user's real 3 kg → ~700 g run.

### Step C3 — Wire distill inputs
**TL;DR:** Make the 5 distill inputs re-run `calculateDistill()` whenever they change.
**File:** `calculator/templates/calculator/index.html` (`<script>`)
**Change:** Add the five distill input ids to a `debouncedDistill = debounce(calculateDistill,120)`
listener block, same pattern as compound inputs.
**Verify:** Editing any distill input recalculates live; invalid combo (collection ABV ≤ target) shows warning placeholder.

---

## PHASE D — Compound content (optional, low risk)

### Step D1 — Seed Aquavit + Absinthe
**TL;DR:** Add two new recipes (with their `category`) to the seed data so the dropdown grows.
**File:** `calculator/fixtures/famous_gin_recipes.json` (or a new `famous_spirit_recipes.json`)
**Change:** Add two recipes with `category` set (`aquavit`, `absinthe`) and their botanical
bills. If the seeding command keys URLs by name, add their image URLs in the command dict too.
**Verify:** `python manage.py create_famous_recipes` then the dropdown shows them; selecting recalculates.

---

## PHASE E — Tests

### Step E1 — Fix model-rename fallout
**TL;DR:** Make sure the existing view tests still pass after the rename.
**File:** `tests/test_calculator_views.py`
**Change:** `GinRecipe` → `Recipe` already done in A3; confirm `get_recipe` assertions still
pass. Remove any `water_for_maceration` API assertion if the view doesn't return that key.
**Verify:** `python manage.py test calculator tests.test_calculator_views`

### Step E2 — Distill calc test (behavioral, not formula-replicating)
**TL;DR:** Add a UI test that just checks distill results get filled in (no hard-coded number).
**File:** `tests/test_ui.py`
**Change:** Add `test_distill_mode_calculates`: switch to Distill mode, fill defaults, assert
`#d-distillate` and `#d-pure-alcohol` are populated (not `—`). Do NOT hard-code the number
(avoid the brittle-assertion anti-pattern from the prior test cleanup).
**Verify:** `python -m pytest tests/test_ui.py -k distill`

### Step E3 — Full suite
**TL;DR:** Run everything and confirm green before finishing.
**Verify:**
```bash
python manage.py test calculator
python -m pytest tests/
```

---

## Architecture notes
- Distill mode is intentionally **DB-free** in v1 — a rakia "recipe" is just wash params, not a
  botanical bill. If you later want saved wash profiles, add a `WashProfile` model then.
- Both modes converge on the same dilution math (`pure_alcohol / target_abv`). If you extract
  a shared `proofTo(pureAlcohol, targetAbv)` helper, reuse it in both `calculateLocally` and
  `calculateDistill`.
- Cut guidance is advisory (like "Est. Water varies") — real cuts depend on nose/temperature,
  not a formula. Keep it as a note, never a hard number.

## Out of scope
- Renaming the `gin_calculator/` Django project package
- Fermentation calculations (sugar → potential ABV) — wash ABV is user-estimated
- Aging / barrel calculations
- Saving distill-mode runs to the DB
