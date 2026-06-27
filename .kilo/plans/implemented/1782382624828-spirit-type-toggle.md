# Spirit Type Toggle — Implementation Plan

## Goal
Add a spirit-type toggle to the Parameters card so users can select between Neutral / food-grade and Home-distilled spirit. Each mode applies a configurable still-yield factor and shows an extra "Spirit to load into still" result stat.

## Decisions
- Two toggle options: **Neutral / food-grade** (default) and **Home-distilled spirit**
- Inline hint text always visible beneath each option (no JS tooltip needed)
  - Neutral: *~10–15% losses · Cut off at ~92°C*
  - Home-distilled: *~30–35% losses · Cut off at ~88–90°C*
- **Still yield %** input is editable in both modes; defaults switch on toggle change (85% neutral, 65% home-distilled)
- "Input spirit ABV" label changes dynamically to "Hearts cut ABV" in home-distilled mode
- **"Spirit to load into still"** result stat shown in both modes = `spirit_needed / (yield_pct / 100)`
- Backend accepts `spirit_type` + `still_yield` and applies yield factor

## Calculation
```
# Existing (unchanged)
spirit_needed = (desired_volume × target_abv/100) / (input_spirit_abv/100)
water_to_add  = desired_volume - spirit_needed

# New
spirit_to_load = spirit_needed / (still_yield / 100)
```

## Files & Steps

### Step 1 — `calculator/views.py`
**Change:** Accept `still_yield` param (float, default `100.0`); compute and return `spirit_to_load = round(spirit_needed / (still_yield / 100), 2)` in the JSON response. Accept `spirit_type` param but no branching logic needed — yield factor encapsulates all behaviour.

**Verify:** `python manage.py test calculator` passes; manually POST `{"volume":1,"recipe_id":1,"input_spirit_abv":96,"target_abv":40,"still_yield":65}` and confirm `spirit_to_load ≈ 0.65`.

---

### Step 2 — `calculator/templates/calculator/index.html` — toggle + yield input HTML
**Change:** Inside the Parameters card `.card-body`, before the existing fields, add:
- A `<div class="field">` containing two radio-style buttons (styled as a segmented control) for spirit type, each with inline hint text beneath
- A `<div class="field" id="yield-field">` for the editable still-yield % input (shown in both modes)

New elements needed:
```html
<!-- spirit type toggle -->
<div class="field">
  <label>Spirit type</label>
  <div class="spirit-toggle">
    <label class="spirit-option">
      <input type="radio" name="spirit_type" value="neutral" checked>
      <span class="spirit-option-label">Neutral / food-grade</span>
      <span class="spirit-option-hint">~10–15% losses · Cut off at ~92°C</span>
    </label>
    <label class="spirit-option">
      <input type="radio" name="spirit_type" value="home">
      <span class="spirit-option-label">Home-distilled spirit</span>
      <span class="spirit-option-hint">~30–35% losses · Cut off at ~88–90°C</span>
    </label>
  </div>
</div>

<!-- still yield input -->
<div class="field" id="yield-field">
  <label for="still_yield">Still yield</label>
  <div class="input-with-unit">
    <input type="number" id="still_yield" value="85" min="10" max="100" step="1">
    <span class="unit-badge">%</span>
  </div>
</div>
```

**Verify:** Page renders without JS errors; both radio options visible with hint text; yield field present.

---

### Step 3 — `calculator/templates/calculator/index.html` — CSS for spirit toggle
**Change:** Add CSS rules (inside the existing `<style>` block or inline in the file's existing pattern — this project has no inline `<style>`, so add to `calculator.css` instead — see Step 3a below).

Actually: CSS goes in the CSS file (Step 3a), not the template.

---

### Step 3a — `calculator/static/calculator/calculator.css`
**Change:** Append CSS for `.spirit-toggle`, `.spirit-option`, `.spirit-option-label`, `.spirit-option-hint`, and the checked-state highlight. Keep it consistent with existing card/field visual language (use CSS variables already defined).

Key rules:
```css
.spirit-toggle {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.spirit-option {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: border-color var(--transition), background var(--transition);
  gap: 2px;
}
.spirit-option:has(input:checked) {
  border-color: var(--color-accent);
  background: var(--color-accent-dim);
}
.spirit-option input[type="radio"] { display: none; }
.spirit-option-label {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--color-text-primary);
}
.spirit-option-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
```

**Verify:** Both options render as styled cards; selected option highlights in accent colour; hint text visible and muted.

---

### Step 4 — `calculator/templates/calculator/index.html` — JS logic
**Change:** Update the inline `<script>`:

1. Add `onSpiritTypeChange()` function triggered by radio `change` event:
   - Sets `still_yield` default to `85` (neutral) or `65` (home-distilled)
   - Updates `#input_spirit_abv` label text: "Input spirit ABV" ↔ "Hearts cut ABV"
   - Calls `calculateLocally()`

2. Update `calculateLocally()`:
   - Read `still_yield` from `#still_yield` input
   - Compute `spiritToLoad = Math.round((spiritNeeded / (stillYield / 100)) * 100) / 100`
   - Pass `spirit_to_load` to `renderResults()`

3. Update `renderResults()`:
   - Add a third `.volume-stat` cell "Spirit to load" showing `data.spirit_to_load`

4. Wire `still_yield` input to `calculateLocally()` in the existing `forEach` event listener block.

5. Wire radio inputs to `onSpiritTypeChange()`.

**Verify:** Switching to home-distilled updates label, changes yield to 65, recalculates; "Spirit to load" stat updates live; switching back restores neutral defaults.

---

### Step 5 — `calculator/templates/calculator/index.html` — volumes grid layout
**Change:** The volumes grid currently has `grid-template-columns: 1fr 1fr` for two stats. With three stats, update to `grid-template-columns: 1fr 1fr 1fr` (or `repeat(3, 1fr)`). Add the new `.volume-stat.still` cell for "Spirit to load" with amber colouring (reuse `--color-amber` / `--color-amber-dim` already defined).

**Verify:** Three stat cells render side-by-side on desktop; stack correctly on mobile (responsive breakpoint already handles `1fr` columns at ≤420px).

---

### Step 6 — `calculator/tests.py`
**Change:** Add a new test class `SpiritTypeCalculationTest` with:
- `test_neutral_spirit_no_yield_loss` — POST with `still_yield=100`, verify `spirit_to_load == spirit_needed`
- `test_neutral_spirit_with_yield` — POST with `still_yield=85`, verify `spirit_to_load = spirit_needed / 0.85`
- `test_home_distilled_yield_65` — POST with `still_yield=65`, verify `spirit_to_load ≈ spirit_needed / 0.65`
- `test_still_yield_missing_defaults_to_100` — POST without `still_yield`, verify `spirit_to_load == spirit_needed`

**Verify:** `python manage.py test calculator` — all new tests pass.

## Validation
```bash
python manage.py check
python manage.py test calculator
python -m pytest tests/
```

## Out of scope
- Persisting the selected spirit type per-recipe or per-user
- Admin UI changes
- Mobile layout beyond what existing responsive breakpoints already handle
