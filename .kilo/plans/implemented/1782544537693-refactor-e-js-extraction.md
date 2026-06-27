# Refactor E: Extract Inline JavaScript to Static Files

Prerequisite: Plans A–D complete and green.

**Risk: HIGH.** This restructures 547 lines of inline JS across 6 new files. Run the full gate after every single step. If any Playwright test fails, stop and report — do not continue.

Full gate command (run after every step):
```
pyenv activate gin && python manage.py check && python manage.py test calculator && python -m pytest tests/
```

---

## Context

`calculator/templates/calculator/index.html` is ~858 lines. Lines 310–856 are inline JavaScript. The JS consists of logically separate concerns:

| Module | Functions |
|--------|-----------|
| `theme.js` | `initTheme`, `updateThemeIcon`, `toggleTheme` |
| `state.js` | `saveState`, `restoreState`, `getCurrentMode`, `setMode` |
| `calculator.js` | `calculateLocally`, `calculateDistill`, `parseVariation`, `debounce` |
| `render.js` | `renderResults`, `renderRecipeImage`, `renderRecipeDescription`, `escHtml` |
| `still-dropdown.js` | `STILL_PRESETS`, `renderStillDropdown`, `selectStill`, `openStillDropdown`, `closeStillDropdown`, `toggleStillDropdown` |
| `main.js` | `onRecipeChange`, `loadRecipeDetails`, `positionTooltip`, `hideTooltip`, all event wiring, `window.addEventListener('load', ...)` entry point |

**Critical constraints:**
- `still-dropdown.js` must NOT use `{% static %}` tags. Replace `{% static "calculator/images/still-vevor.jpg" %}` etc. with hardcoded `/static/calculator/images/still-vevor.jpg`.
- Each JS file must attach its public functions to `window` (e.g., `window.toggleTheme = toggleTheme`) so they are accessible across files without a bundler.
- The inline bootstrap block (language strings `window.__lang`, `window.__t`, function `t(key)`) must remain inline in the HTML — it is template-rendered.
- Load order of script tags must match dependency order: theme → state → calculator → render → still-dropdown → main.

---

## Step 1

**File:** `calculator/static/calculator/js/theme.js` (NEW, ~30 lines)  
**Change:** Extract `initTheme`, `updateThemeIcon`, `toggleTheme` from the inline JS. Attach `window.toggleTheme = toggleTheme`. Call `initTheme()` on `DOMContentLoaded`.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 2

**File:** `calculator/static/calculator/js/state.js` (NEW, ~45 lines)  
**Change:** Extract `saveState`, `restoreState`, `getCurrentMode`, `setMode`. Attach all four to `window`.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 3

**File:** `calculator/static/calculator/js/calculator.js` (NEW, ~85 lines)  
**Change:** Extract `calculateLocally`, `calculateDistill`, `parseVariation`, `debounce`. Attach all four to `window`.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 4

**File:** `calculator/static/calculator/js/render.js` (NEW, ~75 lines)  
**Change:** Extract `renderResults`, `renderRecipeImage`, `renderRecipeDescription`, `escHtml`. Attach all four to `window`.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 5

**File:** `calculator/static/calculator/js/still-dropdown.js` (NEW, ~70 lines)  
**Change:** Extract `STILL_PRESETS` object and `renderStillDropdown`, `selectStill`, `openStillDropdown`, `closeStillDropdown`, `toggleStillDropdown`. Replace any `{% static "..." %}` template tags with `/static/...` hardcoded paths. Attach all public functions to `window`.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 6

**File:** `calculator/static/calculator/js/main.js` (NEW, ~80 lines)  
**Change:** Extract `onRecipeChange`, `loadRecipeDetails`, `positionTooltip`, `hideTooltip`, all event listener wiring, and the `window.addEventListener('load', ...)` entry point.  
**Verify:** File exists. `python manage.py check` passes.

---

## Step 7

**File:** `calculator/templates/calculator/index.html`  
**Change:**
1. Remove lines 310–856 (all inline JS except the bootstrap block).
2. Keep the inline `<script>` block that sets `window.__lang`, `window.__t`, and defines `function t(key)`.
3. At the end of `<body>`, add these script tags in order:
   ```html
   <script src="{% static 'calculator/js/theme.js' %}"></script>
   <script src="{% static 'calculator/js/state.js' %}"></script>
   <script src="{% static 'calculator/js/calculator.js' %}"></script>
   <script src="{% static 'calculator/js/render.js' %}"></script>
   <script src="{% static 'calculator/js/still-dropdown.js' %}"></script>
   <script src="{% static 'calculator/js/main.js' %}"></script>
   ```

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`

Then manually open `http://localhost:8000` and confirm:
- Page renders correctly
- Recipe dropdown changes update description/image
- Volume/ABV inputs trigger calculation
- Mode switch (Distill tab) works
- Still dropdown opens and populates inputs
- Theme toggle works
- Language switch works and state is preserved across reload
- Browser devtools Network tab shows JS loading from `/static/calculator/js/`

---

## Step 8 — Full gate

**Verify:** `python manage.py check && python manage.py test calculator && python -m pytest tests/`  
All must pass. This is the final gate for the entire refactoring sequence.
