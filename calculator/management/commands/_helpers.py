from django.contrib.auth.models import User
from calculator.models import Ingredient, RecipeIngredient


def get_superuser(cmd):
    """Return the first superuser, or print a warning and return None."""
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        cmd.stdout.write(cmd.style.WARNING(
            'No superuser found. Please create a superuser first with: '
            'python manage.py createsuperuser'
        ))
    return admin_user


def create_recipe_ingredients(recipe, ingredients_data):
    """Create RecipeIngredient rows for the given recipe.

    ingredients_data: list of dicts with keys: name, amount, order,
                      and optionally is_optional (default False), notes (default '').
    """
    created = 0
    for data in ingredients_data:
        ingredient, _ = Ingredient.objects.get_or_create(name=data['name'])
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=data['amount'],
            order=data.get('order', 0),
            is_optional=data.get('is_optional', False),
            notes=data.get('notes', ''),
        )
        created += 1
    return created
