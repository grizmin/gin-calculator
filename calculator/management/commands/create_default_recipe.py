from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calculator.models import GinRecipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Create default gin recipe'

    def handle(self, *args, **options):
        # Get or create a default user (usually the first superuser)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('No superuser found. Please create a superuser first with: python manage.py createsuperuser')
            )
            return

        # Check if default recipe already exists
        if GinRecipe.objects.filter(name="Classic London Dry").exists():
            self.stdout.write(
                self.style.WARNING('Default recipe "Classic London Dry" already exists.')
            )
            return

        # Create the default recipe
        recipe = GinRecipe.objects.create(
            name="Classic London Dry",
            description="A traditional London Dry gin recipe with juniper, coriander, and complementary botanicals.",
            base_volume=1.0,
            abv_volume=1.15,
            is_active=True,
            is_default=True,
            created_by=admin_user
        )

        # Create the ingredients
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

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created default recipe "{recipe.name}" with {len(ingredients)} ingredients.')
        )
