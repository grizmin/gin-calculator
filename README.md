# Gin Ingredients Calculator

A Django web application for scaling gin recipe ingredients based on desired volume, with admin recipe management.

## Features

- Calculate scaled ingredients for any volume of gin
- Admin interface for managing multiple gin recipes
- Recipe selection for users
- Clean, responsive web interface
- Real-time calculations with AJAX
- Precise ingredient scaling
- Support for optional ingredients and notes

## Base Recipe (1 Liter)

- **ABV Volume:** 1.15 liters
- **Juniper Berries:** 33g
- **Coriander Seeds:** 8g
- **Angelica Root:** 0.7g
- **Lemon Peel:** 8g
- **Cucumber:** 30g
- **Peppercorns:** 2.5g

## Quick Start with Docker 🐳

The fastest way to get started:

```bash
# Clone and navigate to the project
cd ~/Projects/gin-calculator

# Make build script executable
chmod +x build-and-run.sh

# Build and run with Docker
./build-and-run.sh
```

**Access the app**: http://localhost:8000  
**Admin interface**: http://localhost:8000/admin (admin/admin123)

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

## Manual Setup

1. **Navigate to the project directory:**
   ```bash
   cd ~/Projects/gin-calculator
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser account:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create the default recipe:**
   ```bash
   python manage.py create_default_recipe
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Open your browser and visit:**
   ```
   http://127.0.0.1:8000/
   ```

9. **Access admin interface (optional):**
   ```
   http://127.0.0.1:8000/admin/
   ```

## Usage

### For Regular Users:
1. Select a gin recipe from the dropdown
2. Enter your desired volume in liters
3. Click "Calculate Ingredients" to get scaled amounts
4. The app will show the exact amounts needed for each ingredient

### For Administrators:
1. Access the admin interface at `/admin/`
2. Login with your superuser credentials
3. Navigate to "Gin Recipes" to manage recipes
4. Add new recipes with custom ingredients
5. Set one recipe as default for new users
6. Mark recipes as active/inactive

## Project Structure

```
gin-calculator/
├── manage.py
├── requirements.txt
├── gin_calculator/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── calculator/
    ├── __init__.py
    ├── apps.py
    ├── views.py
    ├── urls.py
    ├── models.py
    ├── admin.py
    ├── tests.py
    └── templates/
        └── calculator/
            └── index.html
```

## API Endpoints

- **POST /calculate/** - Calculate scaled ingredients
  - Request body: `{"volume": 2.0, "recipe_id": 1}`
  - Response: Scaled ingredient amounts and ABV volume

- **POST /get-recipe/** - Get recipe details
  - Request body: `{"recipe_id": 1}`
  - Response: Recipe information with ingredients

## Recipe Management

### Admin Features:
- Create multiple gin recipes with custom names and descriptions
- Add ingredients with amounts, optional status, and notes
- Set base volume and ABV volume for each recipe
- Mark recipes as active/inactive
- Set one recipe as the default
- Order ingredients for consistent display

### Database Models:
- **GinRecipe**: Stores recipe metadata (name, description, volumes, status)
- **RecipeIngredient**: Stores individual ingredients with amounts and properties

## Management Commands

- **create_default_recipe**: Creates the default "Classic London Dry" recipe
  ```bash
  python manage.py create_default_recipe
  ```
