from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calculator.models import GinRecipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Create a custom default gin recipe with specified ABV percentage'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Recipe name')
        parser.add_argument('--abv-percentage', type=float, help='ABV percentage (10-99\\%)')
        parser.add_argument('--base-volume', type=float, default=1.0, help='Base volume in liters')
        parser.add_argument('--description', type=str, help='Recipe description')
        parser.add_argument('--ingredients', nargs='+', help='Ingredients in format "name:amount"')

    def handle(self, *args, **options):
        # Get or create a default user (usually the first superuser)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('No superuser found. Please create a superuser first with: python manage.py createsuperuser')
            )
            return

        # Check if default recipe already exists
        if GinRecipe.objects.filter(is_default=True).exists():
            old_default = GinRecipe.objects.get(is_default=True)
            self.stdout.write(
                self.style.WARNING(f'Existing default recipe "{old_default.name}" will be replaced.')
            )

        # Use provided name or default to "Classic London Dry"
        recipe_name = options.get('name') or "Classic London Dry"
        
        # Use provided ABV percentage or default to 40.0
        abv_percentage = options.get('abv_percentage') or 40.0
        
        # Validate ABV percentage
        if abv_percentage < 10 or abv_percentage > 99:
            self.stdout.write(
                self.style.ERROR('ABV percentage must be between 10 and 99')
            )
            return

        # Use provided description or default to a standard description
        description = options.get('description') or "A traditional gin recipe with juniper, coriander, and complementary botanicals."

        # Create the recipe with ABV percentage (calculating ABV volume)
        abv_volume = (abv_percentage * options.get('base_volume', 1.0)) / 100

        recipe = GinRecipe.objects.create(
            name=recipe_name,
            description=description,
            base_volume=options.get('base_volume', 1.0),
            abv_volume=abv_volume,
            target_abv_percentage=abv_percentage,
            is_active=True,
            is_default=True,
            created_by=admin_user
        )

        # Create ingredients based on command line arguments or use defaults
        if options.get('ingredients'):
            # Parse ingredients from command line input
            ingredients = []
            for ingredient_str in options.get('ingredients'):
                try:
                    name, amount = ingredient_str.split(':')
                    ingredients.append({
                        'name': name.strip(),
                        'amount': float(amount.strip()),
                        'order': len(ingredients) + 1
                    })
                except ValueError:
                    self.stdout.write(
                        self.style.WARNING(f'Invalid ingredient format: {ingredient_str}. Skipping.')
                    )
        else:
            # Use default ingredients
            ingredients = [
                {'name': 'Juniper Berries', 'amount': 33.0, 'order': 1},
                {'name': 'Coriander Seeds', 'amount': 8.0, 'order': 2},
                {'name': 'Angelica Root', 'amount': 0.7, 'order': 3},
                {'name': 'Lemon Peel', 'amount': 8.0, 'order': 4},
                {'name': 'Cucumber', 'amount': 30.0, 'order': 5},
                {'name': 'Peppercorns', 'amount': 2.5, 'order': 6},
            ]

        # Create the ingredients
        for ingredient_data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                name=ingredient_data['name'],
                amount=ingredient_data['amount'],
                order=ingredient_data['order'],
                is_optional=False
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created custom default recipe "{recipe.name}" with {len(ingredients)} ingredients.')
        )