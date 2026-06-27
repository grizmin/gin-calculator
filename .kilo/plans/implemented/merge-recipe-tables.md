# Merge Base Recipe and Calculated Recipe Tables

Combine the base recipe reference table and calculated recipe table into a single unified view showing `calculated / base` format, with base amounts de-emphasized and tooltips.

## Steps

File: `calculator/views.py` (line 25-88)  
Change: Modify `calculate()` to include base ingredient amounts in response  
Verify: `python manage.py test calculator` (tests still pass)

File: `calculator/templates/calculator/index.html` (line 137-148)  
Change: Remove the separate "Base recipe reference" card section  
Verify: Template has no syntax errors (`python manage.py check`)

File: `calculator/templates/calculator/index.html` (line 269-300)  
Change: Remove `renderReferenceRecipe()` function  
Verify: No undefined function calls in remaining code

File: `calculator/templates/calculator/index.html` (line 326-352)  
Change: Rewrite `renderResults()` to merge base and calculated amounts as `calculated / base` format with de-emphasized base  
Verify: Calculate action in browser shows merged table with both values

File: `calculator/templates/calculator/index.html` (line 208-232)  
Change: Remove `renderReferenceRecipe()` call from `loadRecipeDetails()`  
Verify: Recipe selection loads without errors

File: `calculator/static/calculator/calculator.css`  
Change: Add styles for merged ingredient rows: base amount de-emphasis, hover tooltip styling  
Verify: Hover over base amount shows tooltip, base is lighter/smaller than calculated
