# Merge Base Recipe & Calculated Recipe Tables — Detailed Plan

**Executor model:** Qwen Coder 30B

**Goal:** Combine two recipe ingredient tables into one unified table showing calculated amounts and base amounts in `calculated / base` format, with base amounts de-emphasized and tooltips.

**Current state:**
- Base recipe (1L reference) shown in separate "Base recipe reference" card (HTML lines 137-148)
- Calculated recipe shown in "Botanicals" card with `renderResults()` function
- Two separate `renderReferenceRecipe()` and `renderResults()` functions

**Target state:**
- Single "Botanicals" card with merged ingredient rows
- Each row shows: `12.5g / 8g` (calculated / base) with base lighter/smaller
- Base amount has hover tooltip: "Base recipe (1L)"
- No separate reference recipe card

---

## Step 1: Update calculate() endpoint to include base amounts

**File:** `calculator/views.py` (lines 25-88)

**Context:** The `calculate()` function returns scaled ingredients for desired volume. Currently `scaled_ingredients` contains only the calculated amount. We need to add the base amount (1L reference) for each ingredient.

**Change:**
- In the loop at lines 46-54, modify each ingredient dict to include `base_amount` field
- Example: `{'name': 'juniper', 'amount': 12.5, 'base_amount': 8, 'is_optional': False, 'notes': '...'}`

**Specific action:**
Modify lines 46-54 (the ingredient scaling loop):
```python
for ri in recipe.ingredients.select_related('ingredient').all():
    scaled_amount = round(ri.amount * scale_factor, 2)
    scaled_ingredients.append({
        'name': ri.ingredient.name,
        'amount': scaled_amount,
        'base_amount': ri.amount,  # ADD THIS LINE (the 1L reference amount)
        'is_optional': ri.is_optional,
        'notes': ri.notes
    })
```

**Verify:** `python manage.py test calculator` — all tests pass

---

## Step 2: Remove the separate "Base recipe reference" card from HTML

**File:** `calculator/templates/calculator/index.html` (lines 137-148)

**Context:** This card displays the base recipe separately. After merging, we don't need it anymore.

**Change:** Delete lines 137-148 entirely (the `{% if default_recipe %}` section with the reference-recipe-content div)

**Verify:** `python manage.py check` — no template syntax errors

---

## Step 3: Delete the renderReferenceRecipe() function

**File:** `calculator/templates/calculator/index.html` (lines 269-300)

**Context:** This function renders the separate base recipe table. We no longer need it since base amounts are now merged into calculated results.

**Change:** Delete the entire `renderReferenceRecipe()` function (lines 269-300)

**Verify:** Remaining code still references only existing functions

---

## Step 4: Remove renderReferenceRecipe() call from loadRecipeDetails()

**File:** `calculator/templates/calculator/index.html` (line 222)

**Context:** The `loadRecipeDetails()` function calls three render functions. One of those is `renderReferenceRecipe()` which we just deleted.

**Change:** Remove line 222: `renderReferenceRecipe(data.recipe);`

**Verify:** Recipe selection in browser loads without JavaScript errors (check console)

---

## Step 5: Rewrite renderResults() to display merged ingredient rows

**File:** `calculator/templates/calculator/index.html` (lines 326-352)

**Context:** The `renderResults()` function currently displays only calculated amounts. We need to rewrite it to show both calculated and base amounts in the format: `calculated / base`.

**Data available:**
- `data.scaled_ingredients` now has: `{name, amount, base_amount, is_optional, notes}`
- Example: `{name: 'juniper', amount: 12.5, base_amount: 8, is_optional: false, notes: '...'}`

**Change:** Rewrite the ingredient rendering (lines 332-346) to:
1. Display amount as: `<span class="ingredient-amount">${ing.amount} / ${ing.base_amount}</span>`
2. Wrap base amount in a span with class `ingredient-base-amount` so we can style it separately
3. Add a title attribute for hover tooltip: `title="Base recipe (1L)"`

**Specific template structure:**
```html
<span class="ingredient-amount">${ing.amount}</span>
<span class="ingredient-base-amount" title="Base recipe (1L)"> / ${ing.base_amount}</span>
<span class="ingredient-unit">g</span>
```

**Verify:** Click Calculate in browser, verify ingredients show both amounts in format `12.5 / 8`

---

## Step 6: Add CSS styling for merged ingredient display

**File:** `calculator/static/calculator/calculator.css`

**Context:** We need to style the merged ingredient rows. Specifically:
1. Base amount should be visually de-emphasized (lighter color, smaller text)
2. Hover tooltip should be styled appropriately
3. The separation (` / `) between amounts should be visible but subtle

**Change:** Add new CSS rules at end of file (after line 698):

```css
/* ── Merged ingredient amounts (calculated / base) ── */
.ingredient-base-amount {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-weight: 400;
}

.ingredient-base-amount[title] {
  cursor: help;
  text-decoration-color: var(--color-border-subtle);
}

.ingredient-base-amount:hover {
  text-decoration: underline dotted var(--color-border-subtle);
}
```

**Verify:** Open browser, hover over base amount (after `/`), see underline appear

---

## Step 7: Test the complete flow

**File:** None (verification only)

**Context:** Need to ensure the entire merge works end-to-end.

**Manual test steps:**
1. Load page: verify base recipe section is gone, only "Botanicals" card exists
2. Select a recipe from dropdown: no errors
3. Click Calculate with volume=1L: see only base amounts (should match since 1L/1L = same)
4. Change volume to 2L and Calculate: see `amount1 / amount2` format, base lighter
5. Hover over base amount: see dotted underline appear
6. Check browser console: no JavaScript errors

**Verify:** All steps pass without errors

---

## Notes for Executor

- Do NOT modify models.py — data structure stays the same, only the JSON response changes
- Do NOT modify the CSS for `.ingredient-row` itself — keep existing hover/styling intact
- The existing `ingredient-unit` class already exists and styles well, no changes needed
- Keep all existing functionality (optional badges, notes, etc.) — only add base amount display
- The `escHtml()` function is already available for XSS safety — use it for `ing.name` and `ing.notes` (already done in existing code, maintain pattern)
