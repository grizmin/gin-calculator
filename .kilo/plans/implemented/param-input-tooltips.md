# Add Tooltips to Parameter Inputs

## Step 1
**File:** `calculator/templates/calculator/index.html`
**Change:** Add a `title` attribute to each of the four numeric `<input>` elements with a concise explanation:
- `input_spirit_abv`: `title="Alcohol strength of the raw spirit you're starting with (96% for neutral, lower for home-distilled)"`
- `still_yield`: `title="Percentage of liquid recovered from distillation after accounting for losses"`
- `target_abv`: `title="Desired final alcohol percentage of the finished gin after mixing all ingredients"`
- `volume`: `title="Total amount of finished gin you want to produce"`
**Verify:** Open page in browser, hover over each input — native tooltip appears.

## Step 2
**File:** `calculator/static/calculator/calculator.css`
**Change:** Add a subtle cursor hint so inputs look tooltip-able: `.params-input { cursor: help; }` — or skip if native `title` is sufficient (browsers show it automatically).
**Verify:** No visual regression.
