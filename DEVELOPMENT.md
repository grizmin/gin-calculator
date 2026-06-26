# Development & Technical Documentation

For developers and contributors working on the Gin Calculator codebase.

## Project Structure

```
gin-calculator/
├── manage.py
├── requirements.txt
├── gin_calculator/
│   ├── __init__.py
│   ├── settings.py          # Django configuration (env var based)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── calculator/
│   ├── __init__.py
│   ├── apps.py
│   ├── views.py             # API endpoints (/get-recipe/)
│   ├── urls.py
│   ├── models.py            # GinRecipe, Ingredient, RecipeIngredient
│   ├── admin.py             # Django admin interface
│   ├── tests.py
│   ├── management/commands/ # Recipe-seeding commands
│   ├── static/calculator/   # calculator.css
│   └── templates/
│       └── calculator/
│           └── index.html   # Main UI template with JS calculations
└── tests/                   # Playwright UI tests
    ├── conftest.py
    └── test_ui.py
```

## API Endpoints

### GET `/` 
Main calculator page (HTML template)

### POST `/get-recipe/`
Get recipe details for the frontend.
- **Request body:** `{"recipe_id": 1}`
- **Response:**
  ```json
  {
    "success": true,
    "recipe": {
      "id": 1,
      "name": "Classic London Dry",
      "description": "...",
      "image_url": "https://...",
      "base_volume": 1.0,
      "target_abv_percentage": 40,
      "ingredients": [
        {"name": "Juniper", "amount": 33, "is_optional": false, "notes": "..."}
      ]
    }
  }
  ```

**Note:** All calculations happen client-side in JavaScript (`calculateLocally()` in `index.html`). There is no calculation endpoint — changes to parameters trigger instant recalculation in the browser.

## Calculation Logic

All calculations are client-side in `calculator/templates/calculator/index.html`:

```javascript
// Input parameters (from user)
const volume;                // Desired volume (L)
const inputSpiritAbv;        // Input spirit ABV (%)
const macerationAbv;         // Target ABV during maceration (%)
const stillYield;            // Still recovery % (0-100)
const targetAbv;             // Final gin ABV (%)

// Computed values
const pureSpritNeeded = (volume * targetAbv/100) / (inputSpiritAbv/100);
const spiritToLoad = pureSpritNeeded / (stillYield/100);
const waterForMaceration = spiritToLoad * (inputSpiritAbv / macerationAbv - 1);
const waterToAdd = volume - pureSpritNeeded;
```

## Database Models

### `GinRecipe`
```python
class GinRecipe(models.Model):
    name: CharField           # Recipe name
    description: TextField    # HTML description with notes
    image_url: URLField       # Wikimedia/external image URL
    base_volume: FloatField   # Base recipe volume (L)
    target_abv_percentage: IntegerField  # Suggested ABV (%)
    abv_volume: FloatField    # Spirit volume in base recipe (L)
    is_active: BooleanField   # Show/hide in UI
    is_default: BooleanField  # Load by default
    created_at: DateTimeField
    updated_at: DateTimeField
```

### `Ingredient`
```python
class Ingredient(models.Model):
    name: CharField(unique=True)  # e.g. "Juniper Berries"
```

### `RecipeIngredient`
```python
class RecipeIngredient(models.Model):
    recipe: ForeignKey(GinRecipe)
    ingredient: ForeignKey(Ingredient)
    amount: FloatField        # Amount in grams for base recipe
    is_optional: BooleanField
    notes: CharField          # e.g. "±5%" for variation ranges
    order: IntegerField       # Display order in UI
```

## Management Commands

### `create_default_recipe`
Creates the default "Classic London Dry" recipe (8 botanicals, 40% ABV target).
```bash
python manage.py create_default_recipe
```

### `create_famous_recipes`
Populates 8 famous gin recipes from `calculator/fixtures/famous_gin_recipes.json`.
Automatically run in Docker on container startup.
```bash
python manage.py create_famous_recipes
```

### `create_custom_default_recipe`
Creates a custom default recipe (prompts for details).
```bash
python manage.py create_custom_default_recipe
```

## Environment Variables

See [README.md](README.md#environment-variables) for configuration details.

Key vars for development:
- `DEBUG=True` (default for local dev)
- `ALLOWED_HOSTS=localhost,127.0.0.1` (for local testing)
- `DATABASE_PATH=/app/db.sqlite3` (SQLite location)

## Testing

### Unit/Integration Tests
```bash
python manage.py test calculator
```

### UI Tests (Playwright)
```bash
# Install Playwright browsers (one-time)
playwright install

# Run tests
python -m pytest tests/test_ui.py
```

Tests verify:
- Page loads correctly
- Input fields are present
- Recipe dropdown is populated
- Calculations produce correct results
- All parameters trigger recalculation

## Running Locally

```bash
# Activate pyenv environment
pyenv activate gin

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create recipes
python manage.py create_default_recipe
python manage.py create_famous_recipes

# Start dev server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` — admin at `/admin/` (create superuser first if needed).

## Git Workflow

- Main branch: `master` (production-ready)
- Docker images built from `master`
- Env vars configured at runtime (not in code)
- Feature branches should pass `python manage.py test` before merging
