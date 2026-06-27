# Fix: Spirit / Water Calculation Bug

## Problem
`calculate` view divides `desired_volume * target_abv%/100` by the raw
`input_spirit_abv` value (e.g. 96) instead of its decimal fraction (0.96).

**Buggy formula (views.py line 54):**
```python
spirit_needed = ((desired_volume * target_abv_percentage) / 100) / input_spirit_abv
```
With inputs 1 L, 96% spirit, 40% target → `spirit_needed = 0.004 L ≈ 0 L` (wrong)

**Correct result:** `spirit_needed = 0.42 L`, `water_to_add = 0.58 L`

## Root Cause
`input_spirit_abv` is a percentage (sent by the frontend as e.g. `96`), so the
denominator must be `input_spirit_abv / 100`, not `input_spirit_abv`.

## Correct Formula
```
spirit_needed = desired_volume * (target_abv_percentage / 100) / (input_spirit_abv / 100)
             = desired_volume * target_abv_percentage / input_spirit_abv
```

---

## Steps

### Step 1 — Fix the formula in `calculator/views.py`

**File:** `calculator/views.py`  
**Change:** Replace line 54 only.

Old:
```python
spirit_needed = ((desired_volume * target_abv_percentage) / 100) / input_spirit_abv
```
New:
```python
spirit_needed = (desired_volume * target_abv_percentage / 100) / (input_spirit_abv / 100)
```

**Verify:** Read back line 54 and confirm the new formula is present.

---

### Step 2 — Tighten the test in `calculator/tests.py`

**File:** `calculator/tests.py`  
**Change:** In `test_calculate_endpoint`, replace the weak assertion:
```python
self.assertGreater(data['spirit_needed'], 0)
```
with a precise assertion:
```python
self.assertAlmostEqual(data['spirit_needed'], 0.42, places=2)
self.assertAlmostEqual(data['water_to_add'], 0.58, places=2)
```

**Verify:** `python manage.py test` — all tests must pass.

---

## Validation

After both steps:
```bash
pyenv activate gin
python manage.py test
```

Expected: all tests pass. Manual spot-check in the UI:
- Desired volume: 1 L, Input spirit ABV: 96%, Target gin ABV: 40%
- Expected output: Spirit ≈ 0.42 L, Water ≈ 0.58 L

## Constraints
- Only modify the two files listed above.
- Do not change the frontend template, models, migrations, or other views.
- Do not reformat unrelated code.
