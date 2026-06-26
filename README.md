# Gin Ingredients Calculator

A Django web application for scaling gin recipe ingredients based on desired volume, with admin recipe management.

## Features

- Calculate scaled ingredients for any volume of gin in real-time
- Admin interface for managing multiple gin recipes
- Recipe selection with automatic calculation on change
- Clean, responsive web interface (dark/light theme)
- Support for still yield and maceration parameters
- Precise ingredient scaling with variation ranges
- Support for optional ingredients and notes
- Containerized deployment (Docker) with environment-based configuration

## Base Recipe (1 Liter)

- **ABV Volume:** 1.15 liters
- **Juniper Berries:** 33g
- **Coriander Seeds:** 8g
- **Angelica Root:** 0.7g
- **Lemon Peel:** 8g
- **Cucumber:** 30g
- **Peppercorns:** 2.5g

## Quick Start with Docker

The fastest way to get started:

```bash
# Clone and navigate to the project
cd ~/Projects/gin-calculator

# Build and run with Docker
docker-compose up
```

**Access the app**: http://localhost:8000  
**Admin interface**: http://localhost:8000/admin (admin/admin123)

**For public/production deployments**, see the **Environment Variables** section below to configure `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `SECRET_KEY`.

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

### Environment Variables

When running in Docker or production, configure these environment variables:

- **`ALLOWED_HOSTS`**: Comma-separated list of allowed hostnames/IPs (default: `localhost,127.0.0.1,0.0.0.0`)
  - Example: `ALLOWED_HOSTS=gin.example.com,192.168.1.100`
  
- **`CSRF_TRUSTED_ORIGINS`**: Comma-separated list of trusted origins for CSRF protection (default: `http://localhost:8000,http://127.0.0.1:8000`)
  - Must include the protocol and port
  - Example: `CSRF_TRUSTED_ORIGINS=https://gin.example.com,https://gin.example.com:8443`
  
- **`DEBUG`**: Set to `False` in production (default: `True`)
  - Example: `DEBUG=False`
  
- **`SECRET_KEY`**: Django secret key for session security (required in production)
  - Generate a secure value and set it
  - Example: `SECRET_KEY=your-random-secret-key-here`
  
- **`DATABASE_PATH`**: Path to SQLite database file (default: `/app/db.sqlite3`)

### Docker Configuration Example

```bash
docker run -d \
  -p 8000:8000 \
  -e ALLOWED_HOSTS=gin.example.com,192.168.1.100 \
  -e CSRF_TRUSTED_ORIGINS=https://gin.example.com \
  -e DEBUG=False \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -v gin_db:/app/db_data \
  -v gin_media:/app/media \
  grizmin/gin-calculator:latest
```

**For UnRAID users**: Add these as environment variables in the container template, setting them to your actual domain/IP and protocol (http/https).

## Manual Setup

1. **Navigate to the project directory:**
   ```bash
   cd ~/Projects/gin-calculator
   ```

2. **Activate the project's pyenv environment:**
   ```bash
   pyenv activate gin
   ```
   (Don't create a new `venv/` — the env is managed with pyenv.)

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
1. Select a gin recipe from the dropdown (calculation happens automatically)
2. Adjust parameters as needed:
   - **Input spirit ABV**: The ABV of your base spirit (e.g. 96% for neutral spirits)
   - **Still yield**: The % of spirit recovered after distillation (e.g. 85% for neutral, 65% for home-distilled)
   - **Maceration ABV**: The target ABV during the maceration phase (default 50%)
   - **Target gin ABV**: The final desired ABV of your finished gin (e.g. 40%)
   - **Desired volume**: Total volume of gin you want to produce
3. Results update in real-time as you change parameters
4. The app shows:
   - **Maceration alc**: Spirit to load for the first maceration phase
   - **Maceration water**: Water to add partway through to dilute to your maceration ABV
   - **Est. Water**: Estimated water needed after distillation (varies with actual output ABV)

### For Administrators:
1. Access the admin interface at `/admin/`
2. Login with your superuser credentials
3. Navigate to "Gin Recipes" to manage recipes
4. Add new recipes with custom ingredients
5. Set one recipe as default for new users
6. Mark recipes as active/inactive

## For Developers

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Project structure and file organization
- API endpoints and request/response formats
- Database models and schemas
- Calculation logic details
- Management commands
- Local development setup
- Testing instructions

## Recipe Management

### Admin Features:
- Create multiple gin recipes with custom names, descriptions, and image URLs
- Add ingredients with amounts, optional status, and notes
- Set base volume and ABV volume for each recipe
- Mark recipes as active/inactive
- Set one recipe as the default
- Order ingredients for consistent display

