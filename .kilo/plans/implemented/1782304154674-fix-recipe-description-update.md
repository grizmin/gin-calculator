# Fix: Recipe description does not update on recipe change

## Problem

`index.html` binds `onchange="onRecipeChange()"` to the recipe `<select>` (line 40), but
`onRecipeChange()` is **never defined** in the page's `<script>` block.

On page load, `loadRecipeDetails({{ default_recipe.id }})` is called with a hardcoded ID,
so the default recipe description shows correctly. When the user switches recipes,
`onRecipeChange()` throws a ReferenceError and nothing updates.

## Affected file

`calculator/templates/calculator/index.html` — script block only (no view, model, or URL changes).

## Decision

When the user switches recipes, **clear/hide the results panel** so stale calculation data
from the previous recipe is not shown alongside the new description.

## Steps

### Step 1 — Add `onRecipeChange()` in the script block

**File:** `calculator/templates/calculator/index.html`

Inside the `<script>` block, add the following function (place it near `loadRecipeDetails`,
e.g. immediately after it):

```js
function onRecipeChange() {
  const recipeId = document.getElementById('recipe_select').value;
  if (!recipeId) return;

  // Clear stale results from the previous recipe
  const panel = document.getElementById('results');
  panel.classList.remove('show');
  document.getElementById('results-placeholder').style.display = '';

  loadRecipeDetails(recipeId);
}
```

**What this does:**
- Reads the newly selected recipe ID from the `<select>`.
- Hides the results panel and restores the placeholder (removing stale data).
- Calls the existing `loadRecipeDetails()` which fetches `/get-recipe/`, updates
  `#recipe-description`, updates the base recipe reference section, and sets `target_abv`.

### Verification after Step 1

```bash
pyenv activate gin
python manage.py runserver
```

1. Open http://127.0.0.1:8000 in a browser.
2. Confirm the default recipe description is visible on load.
3. Switch to a different recipe in the dropdown.
4. Confirm `#recipe-description` updates to the new recipe's name and description.
5. Confirm the base recipe reference table updates.
6. Confirm the results panel is cleared/hidden after switching.
7. Hit Calculate — confirm results appear correctly for the newly selected recipe.

```bash
python manage.py test
```

All existing tests must pass without modification.

## Risks

- None structural. This is a pure addition of a missing function that the template already expects.
- The `results` panel CSS class `show` controls visibility; `panel.classList.remove('show')` matches the existing pattern in `renderResults()` where `panel.classList.add('show')` is used.

## Out of scope

- Adding automated browser/JS tests for this interaction.
- Any changes to views, models, URLs, or CSS.
