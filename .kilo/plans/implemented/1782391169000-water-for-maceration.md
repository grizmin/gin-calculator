# Maceration Alcohol & Water — Implementation Plan

## Goal
Replace the low-value "Pure spirit needed" stat with two maceration-focused stats that
match the user's real 2-phase maceration process: **Maceration alc** (the alcohol you
load to start maceration — renamed from "Spirit to load from still") and **Maceration
water needed** (the water you add partway through to bring the charge down to
maceration strength, e.g. 96% neat for 3hrs → dilute to 50% for another 5-6hrs).
"Pure spirit needed" is dropped from the display — it's a simple-dilution reference
number with no actionable value once maceration/redistillation entered the picture.

## Decisions
- **Drop** the "Pure spirit needed" stat box and its `#spirit-value` element.
  `pure_spirit_needed` is still computed in JS (needed internally for
  `spirit_to_load` and `water_to_add`) — it's just no longer displayed.
- **Rename** "Spirit to load from still" → **Maceration alc**. Same value, same id
  (`spirit-load-value`), same formula (`spirit_to_load`) — just a label-text change,
  since this is literally the alcohol loaded for the first, full-strength phase of
  maceration.
- **New stat: Maceration water needed** = the water added partway through maceration
  to bring the charge down to `maceration_abv`%.
- `.volumes-grid` stays a 3-column row — no CSS layout change needed, since we're
  swapping one stat for another, not adding a 4th.
- **Recolor:** "Maceration water needed" uses the `.water` (green) class instead of
  `.spirit` (blue) — it's literally water, matching the convention already used for
  "Est. Water".
- New input **Maceration ABV** (default `50`, matches the user's universal practice),
  editable, placed in `.params-inputs-row` between "Still yield" and "Target gin ABV".
- Guard: if `maceration_abv <= 0` or `maceration_abv >= input_spirit_abv`, show the
  existing warning-placeholder pattern and skip rendering (can't dilute upward).
- `pure_spirit_needed`, `spirit_to_load`, `water_to_add` formulas: **unchanged**.
- No backend/model changes — same as before.

## Calculation
```
# Existing (unchanged, computed but no longer displayed)
pure_spirit_needed = (desired_volume × target_abv/100) / (input_spirit_abv/100)

# Existing (unchanged), now labeled "Maceration alc"
spirit_to_load = pure_spirit_needed / (still_yield/100)

# Existing (unchanged)
water_to_add = desired_volume - pure_spirit_needed

# New, labeled "Maceration water needed"
water_for_maceration = spirit_to_load × (input_spirit_abv / maceration_abv − 1)
```

## Files & Steps

### Step 1 — `calculator/templates/calculator/index.html` — Maceration ABV input
**Change:** In `.params-inputs-row`, insert a new `.params-group` between the
"Still yield" group and the "Target gin ABV" group:
```html
<div class="params-group">
  <label class="params-label" for="maceration_abv">Maceration ABV</label>
  <div class="params-input-wrap">
    <input class="params-input" type="number" id="maceration_abv" value="50" min="5" max="95" step="0.1" title="ABV to dilute the maceration charge down to partway through (e.g. after the neat phase)">
    <span class="params-unit">%</span>
  </div>
</div>
```

**Verify:** Field renders between Still yield and Target gin ABV, default `50`, no console errors.

---

### Step 2 — `calculator/templates/calculator/index.html` — replace volumes-grid stats
**Change:** Replace the current three `.volume-stat` cells in `.volumes-grid` with:
```html
<div class="volume-stat spirit">
  <div class="volume-stat-label">Maceration alc</div>
  <div class="volume-stat-value">
    <span id="spirit-load-value">—</span><span class="volume-stat-unit">L</span>
  </div>
</div>
<div class="volume-stat water">
  <div class="volume-stat-label">Maceration water needed</div>
  <div class="volume-stat-value">
    <span id="maceration-water-value">—</span><span class="volume-stat-unit">L</span>
  </div>
</div>
<div class="volume-stat water">
  <div class="volume-stat-label">Est. Water</div>
  <div class="volume-stat-value">
    <span id="water-value">—</span><span class="volume-stat-unit">L</span>
  </div>
  <div class="volume-stat-note">varies with distillation output</div>
</div>
```
This removes the `#spirit-value` ("Pure spirit needed") cell entirely.
`spirit-load-value` and `water-value` keep their existing ids — only the label text /
position of the middle cell changes.

**Verify:** Three stat boxes render: Maceration alc, Maceration water needed, Est.
Water. `document.getElementById('spirit-value')` is `null`.

---

### Step 3 — `calculator/templates/calculator/index.html` — compute + render
**Change A:** In `calculateLocally()`, after the existing `const spiritToLoad = ...`
line, add:
```js
const macerationAbv = parseFloat(document.getElementById('maceration_abv').value);

if (!macerationAbv || macerationAbv <= 0 || macerationAbv >= inputSpiritAbv) {
  document.getElementById('results-placeholder').style.display = '';
  document.getElementById('results').classList.remove('show');
  document.getElementById('results-placeholder').innerHTML =
    '<span class="results-placeholder-icon" aria-hidden="true">⚠️</span>' +
    '<p>Maceration ABV must be lower than the input spirit ABV.</p>';
  return;
}

const waterForMaceration = Math.round(
  (spiritToLoad * (inputSpiritAbv / macerationAbv - 1)) * 100
) / 100;
```
Add `maceration_water: waterForMaceration` to the object passed into
`renderResults({...})`.

**Change B:** In `renderResults()`, remove the line
`document.getElementById('spirit-value').textContent = data.spirit_needed;` and add:
```js
document.getElementById('maceration-water-value').textContent = data.maceration_water;
```

**Verify:** In the browser console, with a recipe loaded, `maceration_abv=50`,
`input_spirit_abv=96`: confirm `waterForMaceration` matches
`spiritToLoad × (96/50 − 1)` rounded to 2 decimals, and no error from a missing
`#spirit-value` element.

---

### Step 4 — `calculator/templates/calculator/index.html` — wire input listener
**Change:** Add `'maceration_abv'` to the array in the existing `forEach` block that
wires `debouncedCalculate` to inputs:
```js
['volume', 'input_spirit_abv', 'target_abv', 'still_yield', 'maceration_abv'].forEach(id => {
  document.getElementById(id).addEventListener('input', debouncedCalculate);
});
```

**Verify:** Typing in Maceration ABV recalculates "Maceration water needed" live.
Setting Maceration ABV ≥ Input spirit ABV shows the warning placeholder.

---

### Step 5 — `tests/test_ui.py` — update for removed/renamed stat
**Change:** `test_calculate_formula` currently waits on and asserts
`#spirit-value === '0.63'`, which no longer exists. Update it to wait on
`#spirit-load-value` ("Maceration alc") instead. With the default `still_yield=85`:
`pure_spirit_needed` for 1.5L / 96% / 40% is `0.625` (rounds to `0.63` for display,
but that's no longer shown); `spirit_to_load = 0.625 / 0.85 ≈ 0.74` — that's the new
expected value. The `#water-value` assertion (`0.87`) is unaffected.
```python
page.wait_for_function(
    "() => document.getElementById('spirit-load-value').textContent === '0.74'",
    timeout=5000,
)
spirit_load = page.inner_text("#spirit-load-value")
water = page.inner_text("#water-value")
assert "0.74" in spirit_load, f"Wrong spirit-to-load value: {spirit_load!r}"
assert "0.87" in water, f"Wrong water value: {water!r}"
```

**Verify:**
```bash
python -m pytest tests/test_ui.py -k test_calculate_formula
```

---

### Step 6 — Run full test suite
```bash
pyenv activate gin
python manage.py test calculator
python -m pytest tests/
```

## Validation
```bash
python manage.py check
python manage.py test calculator
python -m pytest tests/
```

## Out of scope
- Persisting Maceration ABV per recipe (it's a process parameter, like still yield)
- Modeling a real distillation ABV curve — `still_yield` stays a flat volume-loss
  factor, same simplification already used for "Maceration alc"
- A post-run "actual measured ABV" override for "Est. Water" (separate idea raised in
  conversation, not part of this plan)
- Any change to the already-removed `/calculate/` endpoint
