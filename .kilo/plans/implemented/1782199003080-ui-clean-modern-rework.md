# UI Clean Modern Rework

## Goal
Visually improve `calculator/templates/calculator/index.html` without touching any Python/Django code. The redesign applies a Clean Modern theme: white background, slate/charcoal typography, indigo accent color, Inter font, Font Awesome icons.

## Constraints
- **Single file changed:** `calculator/templates/calculator/index.html`
- **No Python/Django changes** — views, models, URLs, tests untouched
- **External CDN allowed:** Google Fonts (Inter) + Font Awesome 6 Free
- **Keep** the "Current Recipe Details" base-amounts section (style it to match, don't remove)
- **Executor limit:** write/edit one logical section per step; the file is ~530 lines — break edits into focused, independently verifiable chunks

## Design Decisions
| Decision | Choice |
|---|---|
| Theme | Clean Modern |
| Background | White (`#ffffff`) |
| Primary text | Slate dark (`#1e293b`) |
| Accent / interactive | Indigo (`#4f46e5`) |
| Optional ingredient accent | Amber (`#f59e0b`) |
| Font | Inter (Google Fonts CDN) |
| Icons | Font Awesome 6 Free (CDN) |
| Gradients | Remove all — flat colors only |
| Body background | Light slate (`#f1f5f9`) |

## Steps

### Step 1 — CDN links + CSS variables + typography
**File:** `calculator/templates/calculator/index.html`

In `<head>`, replace the existing `<style>` block's opening lines:
- Add `<link>` for Inter from Google Fonts (`wght@300;400;600;700`)
- Add `<link>` for Font Awesome 6 Free CDN
- Set CSS custom properties on `:root`:
  ```css
  --color-bg: #ffffff;
  --color-surface: #f8fafc;
  --color-border: #e2e8f0;
  --color-text: #1e293b;
  --color-muted: #64748b;
  --color-accent: #4f46e5;
  --color-accent-hover: #4338ca;
  --color-optional: #f59e0b;
  --color-optional-bg: #fffbeb;
  --radius: 10px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
  ```
- Set `body { font-family: 'Inter', sans-serif; background: #f1f5f9; }`

**Verify:** Page loads without JS errors; Inter font renders in browser.

---

### Step 2 — Header
**File:** `calculator/templates/calculator/index.html`

Replace `.header` CSS:
- Flat indigo background (`var(--color-accent)`)
- White text, `font-weight: 300` for h1 (`2rem`), subtitle opacity 0.85
- Remove all `linear-gradient` from header

No HTML changes needed in this step.

**Verify:** Header shows flat indigo band with white text.

---

### Step 3 — Container + input section
**File:** `calculator/templates/calculator/index.html`

Update `.container` CSS:
- `border-radius: var(--radius)`, `box-shadow: var(--shadow)`
- Remove `overflow: hidden` (it clips focus rings)

Update `.input-section` CSS:
- `background: var(--color-surface)`, `border: 1px solid var(--color-border)`

Update `input[type="number"], select` CSS:
- `border-color: var(--color-border)`, focus `border-color: var(--color-accent)`

**Verify:** Input section renders with light gray surface and indigo focus rings.

---

### Step 4 — Volume stepper (+/− buttons)
**File:** `calculator/templates/calculator/index.html`

In the HTML, wrap the `<input type="number" id="volume">` in a stepper div:
```html
<div class="stepper">
  <button type="button" class="stepper-btn" onclick="adjustVolume(-0.1)">−</button>
  <input type="number" id="volume" value="1" min="0.1" max="100" step="0.1">
  <button type="button" class="stepper-btn" onclick="adjustVolume(0.1)">+</button>
</div>
```

Add CSS for `.stepper` (flex row, border wrapping all three), `.stepper-btn` (flat, indigo on hover).

Add JS function:
```js
function adjustVolume(delta) {
  const input = document.getElementById('volume');
  const val = Math.round((parseFloat(input.value) + delta) * 10) / 10;
  if (val >= 0.1 && val <= 100) input.value = val;
}
```

**Verify:** +/− buttons increment/decrement volume; keyboard entry still works; Enter still triggers calculate.

---

### Step 5 — Calculate button + loading state
**File:** `calculator/templates/calculator/index.html`

Update `.calculate-btn` CSS:
- Solid indigo, no gradient, no `transform`
- `:hover` → `background: var(--color-accent-hover)`
- Add `.calculate-btn.loading` → reduced opacity, `cursor: not-allowed`

In `calculateIngredients()` JS:
- On start: `btn.classList.add('loading'); btn.disabled = true; btn.textContent = 'Calculating…'`
- On finish (success or error): restore button text and remove `.loading`

**Verify:** Button shows "Calculating…" and is disabled during fetch; re-enables after response.

---

### Step 6 — Inline error banner (replace alert)
**File:** `calculator/templates/calculator/index.html`

Add HTML element after the button:
```html
<div id="error-banner" class="error-banner" style="display:none"></div>
```

Add CSS for `.error-banner`:
- Red-tinted surface (`#fef2f2`), `border: 1px solid #fecaca`, `border-radius: var(--radius)`
- `padding: 12px 15px`, `color: #dc2626`, `font-size: 0.95rem`

Replace all `alert('...')` calls in JS with:
```js
function showError(msg) {
  const el = document.getElementById('error-banner');
  el.textContent = msg;
  el.style.display = 'block';
}
function clearError() {
  document.getElementById('error-banner').style.display = 'none';
}
```
Call `clearError()` at the start of `calculateIngredients()`.

**Verify:** Invalid volume or failed fetch shows red banner instead of alert dialog.

---

### Step 7 — Recipe info banner
**File:** `calculator/templates/calculator/index.html`

Replace `.recipe-info` CSS:
- Remove blue background; use `background: white`, `border-left: 3px solid var(--color-accent)`
- `color: var(--color-text)`, heading `color: var(--color-accent)`

**Verify:** Recipe description (if present) shows as a clean left-bordered aside.

---

### Step 8 — Ingredient cards
**File:** `calculator/templates/calculator/index.html`

Update `.ingredient-item` CSS:
- `background: white`, `box-shadow: var(--shadow)`, `border-left: 4px solid var(--color-accent)`
- Remove gray background

Update `.ingredient-item.optional`:
- `border-left-color: var(--color-optional)`, `background: var(--color-optional-bg)`

Update `.ingredient-amount`:
- `color: var(--color-accent)`, `font-size: 1.4rem`

Add Font Awesome icon to each card in `displayResults()` JS — prepend a `<i class="fa-solid fa-seedling"></i>` span to `.ingredient-name` (use `fa-lemon` for lemon/citrus if name contains "lemon", `fa-seedling` default).

**Verify:** Cards render white with shadow; optional cards amber-tinted; amounts large and indigo.

---

### Step 9 — ABV card + results section header
**File:** `calculator/templates/calculator/index.html`

Update `.abv-info` CSS:
- Flat indigo (`var(--color-accent)`), white text, `border-radius: var(--radius)`
- Remove gradient

Update `.results h3`:
- `border-bottom-color: var(--color-accent)`

Update `.recipe-title`:
- Replace gradient with flat indigo, `border-radius: var(--radius)`, `letter-spacing: 0.02em`

**Verify:** ABV card shows flat indigo; results section has clean indigo accent border on heading.

---

### Step 10 — Current Recipe Details section restyle
**File:** `calculator/templates/calculator/index.html`

Update `.current-recipe` CSS:
- `background: var(--color-surface)`, `border: 1px solid var(--color-border)`, `border-radius: var(--radius)`

Update `.base-ingredient`:
- `border-bottom-color: var(--color-border)`

**Verify:** Base recipe section renders with light surface and matches card aesthetic.

---

### Step 11 — Mobile responsive cleanup
**File:** `calculator/templates/calculator/index.html`

Review `@media (max-width: 768px)` block:
- Ensure stepper doesn't overflow
- Ensure ingredient grid collapses to single column
- Reduce header h1 to `1.6rem`
- Add `padding: 15px` on `.content` at mobile

**Verify:** Resize browser to 375px width; no horizontal scroll; stepper usable.

---

## Validation
After all steps:
1. `pyenv activate gin && python manage.py test` — must pass with 0 failures
2. Load `http://127.0.0.1:8000/` in browser
3. Select a recipe → recipe info banner appears
4. Enter volume `2.5` → click Calculate → scaled ingredients appear with indigo cards
5. Enter `0` → error banner appears (no alert dialog)
6. Use +/− stepper → volume increments correctly
7. Resize to mobile → no overflow

## Risks
- Font Awesome CDN URL must be valid free-tier link (use `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css`)
- `overflow: hidden` removal on `.container` may expose focus ring clipping fix but should not break layout
- Executor must not touch any `.py` files
