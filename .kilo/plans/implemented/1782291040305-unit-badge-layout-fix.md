# Unit Badge Layout Fix

## Goal
Improve readability of number inputs by repositioning unit badges (L, %) from overlapping absolutely-positioned elements to flex siblings directly next to the inputs.

## Context
- Three number inputs in the parameters card: volume (L), input_spirit_abv (%), target_abv (%)
- Current implementation: unit badges positioned absolutely at `right: 10px`, overlapping spinner buttons
- Input padding-right: 48px wastes space for 2-3 digit numbers
- User feedback: badge should sit immediately next to the input value for compactness and readability

## Current HTML Structure
```html
<div class="input-with-unit">
  <input type="number" id="volume" value="1" ...>
  <span class="unit-badge">L</span>
</div>
```
(Same structure for input_spirit_abv and target_abv)

## Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Badge positioning | Move from `position: absolute` to flex sibling (static positioning) | No overlap, semantic HTML, simpler CSS |
| Spinner visibility | Hide completely (opacity: 0) | Compact layout, unit badge provides context, reduces visual clutter |
| Gap between input and badge | 8px | Balances compactness with readability |
| Badge styling | Keep current (unchanged) | Already minimal, appropriate for compact layout |

## Files to Modify

### Step 1: Update CSS for `.input-with-unit` container

**File**: `calculator/static/calculator/calculator.css`

**Changes:**
1. Remove `position: relative` from `.input-with-unit` (no longer needed for absolute children)
2. Keep `display: flex` and `align-items: center`
3. Add explicit `gap: 8px` for spacing between input and badge

Current (lines 249-253):
```css
.input-with-unit {
  position: relative;
  display: flex;
  align-items: center;
}
```

Change to:
```css
.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}
```

### Step 2: Update CSS for number input within `.input-with-unit`

**File**: `calculator/static/calculator/calculator.css`

**Changes:**
Remove unnecessary right padding since badge is now a flex sibling, not absolutely positioned.

Current (lines 255-258):
```css
.input-with-unit input {
  flex: 1;
  padding-right: 48px;
}
```

Change to:
```css
.input-with-unit input {
  padding: 9px 12px;
}
```

**Rationale:** Input will now be naturally sized based on content + normal padding, not flex-stretched. The unit badge takes up only the space it needs.

### Step 3: Update CSS for `.unit-badge`

**File**: `calculator/static/calculator/calculator.css`

**Changes:**
Remove absolute positioning; make it a static flex item. Add `white-space: nowrap` to prevent badge wrapping.

Current (lines 260-269):
```css
.unit-badge {
  position: absolute;
  right: 10px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  pointer-events: none;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

Change to:
```css
.unit-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  pointer-events: none;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  flex-shrink: 0;
}
```

**Rationale:** 
- Remove `position: absolute` and `right: 10px` (not needed as flex sibling)
- Add `white-space: nowrap` to keep "L", "%", "%" on one line
- Add `flex-shrink: 0` to prevent badge from shrinking if container is constrained

### Step 4: Hide spinner buttons completely

**File**: `calculator/static/calculator/calculator.css`

**Changes:**
Update opacity from 0.4 to 0 for cleaner look in compact layout.

Current (lines 243-246):
```css
.field input[type="number"]::-webkit-inner-spin-button,
.field input[type="number"]::-webkit-outer-spin-button {
  opacity: 0.4;
}
```

Change to:
```css
.field input[type="number"]::-webkit-inner-spin-button,
.field input[type="number"]::-webkit-outer-spin-button {
  opacity: 0;
}
```

**Rationale:** Spinners are no longer needed; users can type directly or use arrow keys. Unit badge now provides all visual context.

## Verification

After changes, verify in browser:
1. Open http://localhost:8000
2. Navigate to the Parameters section
3. Check all three inputs: volume (L), input_spirit_abv (%), target_abv (%)
4. **Visual check:**
   - Badge sits immediately next to input value (not far right)
   - ~8px gap between input border and badge
   - No overlap with spinner buttons
   - Spinner up/down arrows completely hidden
   - Responsive: badges stay next to inputs on resize
5. **Functional check:**
   - Can still change values by typing
   - Can still use arrow keys (keyboard) to increment/decrement
   - Can click and drag (number input drag-to-adjust)
   - Tab navigation works smoothly between inputs
6. **Edge cases:**
   - Values with decimals (e.g., "1.5L", "40.0%") — badges should not wrap
   - Small viewport (mobile) — layout should remain compact

## Risks

- **None identified.** Changes are CSS-only, non-breaking:
  - No JavaScript changes
  - HTML structure unchanged
  - Spinner functionality preserved (users can still increment via keyboard/drag)
  - No content layout shifts (flex layout is robust)

## Notes

- Spinner buttons remain accessible via keyboard (arrow keys) even when hidden (opacity: 0)
- This is a pure CSS refactor with no impact on calculation logic or data flow
- The change is fully responsive and works on all viewport sizes
