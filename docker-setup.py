#!/usr/bin/env python
"""
Docker setup script to initialize database with default user and recipe
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gin_calculator.settings')
django.setup()

from django.contrib.auth.models import User
from calculator.models import GinRecipe, RecipeIngredient

def create_default_setup():
    """Create default admin user and recipe if they don't exist"""
    
    # Create default admin user if no superuser exists
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating default admin user...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Default admin user created: admin/admin123")
    else:
        print("ℹ️ Admin user already exists")
    
    # Create default recipe if it doesn't exist
    if not GinRecipe.objects.filter(name='Classic London Dry').exists():
        print("Creating default recipe...")
        
        # Get the admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Create the recipe
        recipe = GinRecipe.objects.create(
            name='Classic London Dry',
            description='A traditional London Dry gin recipe with juniper, coriander, and complementary botanicals.',
            base_volume=1.0,
            abv_volume=1.15,
            is_active=True,
            is_default=True,
            created_by=admin_user
        )
        
        # Create ingredients
        ingredients = [
            {'name': 'Juniper Berries', 'amount': 33.0, 'order': 1},
            {'name': 'Coriander Seeds', 'amount': 8.0, 'order': 2},
            {'name': 'Angelica Root', 'amount': 0.7, 'order': 3},
            {'name': 'Lemon Peel', 'amount': 8.0, 'order': 4},
            {'name': 'Cucumber', 'amount': 30.0, 'order': 5},
            {'name': 'Peppercorns', 'amount': 2.5, 'order': 6},
        ]
        
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=ingredient_data['name'],
                amount=ingredient_data['amount'],
                order=ingredient_data['order'],
                is_optional=False
            )
        
        print(f"✅ Default recipe '{recipe.name}' created with {len(ingredients)} ingredients")
    else:
        print("ℹ️ Default recipe already exists")

if __name__ == '__main__':
    try:
        create_default_setup()
        print("🍸 Docker setup completed successfully!")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        exit(1)
