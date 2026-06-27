# Auto-Calculate on Recipe/Input Change

## Goal
Replace the manual "Calculate" button with automatic real-time calculation:
- Switching recipe → auto-loads and calculates
- Changing volume, spirit ABV, or target ABV → auto-recalculates
- Page load → default recipe is selected and calculated immediately
- All calculation logic moves client-side (no `/calculate/` fetch needed)

## Files Affected
1. `calculator/templates/calculator/index.html` — HTML + inline JS
2. `calculator/static/calculator/calculator.css` — remove button styles

---

## Step 1 — Remove Calculate button from HTML, update placeholder

**File:** `calculator/templates/calculator/index.html`

**Change:**
- Remove lines 80-82 (the `<button class="btn-calculate" id="calc-btn" ...>` element):
  ```html
  <button class="btn-calculate" id="calc-btn" onclick="calculateIngredients()" type="button">
    Calculate
  </button>
  ```
- Replace placeholder text (line 93) from:
  ```html
  <p>Select a recipe, set your parameters, and hit <strong>Calculate</strong>.</p>
  ```
  To:
  ```html
  <p>Results appear automatically as you adjust parameters.</p>
  ```

**Verify:** Open page in browser — no Calculate button visible, placeholder shows new text.

---

## Step 2 — Remove `.btn-calculate` CSS

**File:** `calculator/static/calculator/calculator.css`

**Change:**
- Delete lines 306-332 (the entire `/* ── Calculate button ── */` block including `.btn-calculate`, `.btn-calculate:hover`, `.btn-calculate:active`).

**Verify:** No CSS errors in browser console.

---

## Step 3 — Replace `calculateIngredients()` with client-side `calculateLocally()`

**File:** `calculator/templates/calculator/index.html`

**Change:**
Replace the entire `calculateIngredients()` function (lines 260-282) with this client-side version:

```js
function calculateLocally() {
    const volume = parseFloat(document.getElementById('volume').value);
    const inputSpiritAbv = parseFloat(document.getElementById('input_spirit_abv').value);
    const targetAbv = parseFloat(document.getElementById('target_abv').value);

    if (!currentRecipe) return;
    if (!volume || volume <= 0) return;
    if (!inputSpiritAbv || inputSpiritAbv <= 0) return;
    if (!targetAbv || targetAbv <= 0) return;

    const scaleFactor = volume / currentRecipe.base_volume;

    const scaledIngredients = currentRecipe.ingredients.map(ing => ({
        name: ing.name,
        amount: Math.round(ing.amount * scaleFactor * 100) / 100,
        base_amount: ing.amount,
        is_optional: ing.is_optional,
        notes: ing.notes
    }));

    const spiritNeeded = Math.round(
        ((volume * targetAbv / 100) / (inputSpiritAbv / 100)) * 100
    ) / 100;
    const waterToAdd = Math.round((volume - spiritNeeded) * 100) / 100;

    renderResults({
        success: true,
        recipe_name: currentRecipe.name,
        spirit_needed: spiritNeeded,
        water_to_add: waterToAdd,
        scaled_ingredients: scaledIngredients
    });
}
```

Also remove the `showError()` function (lines 352-357) — no longer needed since there's no button to display errors on and client-side math won't fail.

**Verify:** Function produces same output as `/calculate/` endpoint for identical inputs. Math: `round(x * 100) / 100` matches server's `round(x, 2)`.

---

## Step 4 — Make `loadRecipeDetails` return data; update `onRecipeChange`, input listeners, and page load

**File:** `calculator/templates/calculator/index.html`

**Change A — `loadRecipeDetails` returns recipe data:**
In the `.then(data => { ... })` block of `loadRecipeDetails` (around line 213), add `return data.recipe;` at the end so the Promise resolves with the recipe object:
```js
.then(data => {
    if (!data.success) { console.error('Recipe load error:', data.error); return; }
    currentRecipe = data.recipe;
    renderRecipeImage(data.recipe);
    renderRecipeDescription(data.recipe);
    const targetInput = document.getElementById('target_abv');
    if (targetInput && data.recipe.target_abv_percentage) {
        targetInput.value = data.recipe.target_abv_percentage;
    }
    return data.recipe;   // <-- ADD THIS
})
```

**Change B — `onRecipeChange` becomes async and triggers calculation:**
Replace `onRecipeChange()` (lines 220-225) with:
```js
async function onRecipeChange() {
    const select = document.getElementById('recipe_select');
    const recipeId = select.value;
    await loadRecipeDetails(recipeId);
    calculateLocally();
}
```

**Change C — Add `input` event listeners on all three parameter fields:**
Replace the volume Enter-key listener (lines 382-384):
```js
document.getElementById('volume').addEventListener('keydown', e => {
    if (e.key === 'Enter') calculateIngredients();
});
```
With input listeners on all three fields:
```js
['volume', 'input_spirit_abv', 'target_abv'].forEach(id => {
    document.getElementById(id).addEventListener('input', calculateLocally);
});
```

**Change D — Page load triggers full calculation:**
Replace the `window.addEventListener('load', ...)` block (lines 387-389):
```js
window.addEventListener('load', () => {
    loadRecipeDetails({{ default_recipe.id }});
});
```
With:
```js
window.addEventListener('load', () => {
    onRecipeChange();
});
```

**Verify:**
- Page loads → default recipe selected, results shown automatically
- Switch recipe → results update for new recipe
- Change any input → results recalculate immediately
- No console errors

---

## Step 5 — Run tests

**Verify:**
```bash
pyenv activate gin
python manage.py test calculator
```

Note: UI tests in `tests/test_ui.py` are already broken (`.calculate-btn` selector doesn't match current code, `#spirit-needed` / `#water-to-add` don't exist). They are out of scope for this change.
