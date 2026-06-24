from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calculator.models import GinRecipe, RecipeIngredient
import json
import os

class Command(BaseCommand):
    help = 'Create famous gin recipes from fixture file'

    def handle(self, *args, **options):
        # Get or create a default user (usually the first superuser)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING('No superuser found. Please create a superuser first with: python manage.py createsuperuser')
            )
            return

        # Exact image URLs per recipe name (source of truth for images).
        IMAGE_URLS = {
            "Tanqueray London Dry": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Tanqueray_bottle.JPG",
            "Hendrick's": "https://upload.wikimedia.org/wikipedia/en/c/c6/Hendricks_Gin_Logo.jpg",
            "Bombay Sapphire": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Bombay_Sapphire_-_bouteilles.JPG",
            "Beefeater London Dry": "https://upload.wikimedia.org/wikipedia/commons/3/37/BEEFEATER2022_%28cropped%29.jpg",
            "Aviation American Gin": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Aviation_American_Gin_Distillery_filling_station.jpg",
            "Gordon's London Dry": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Gordons_London_Dry_Gin_im_Regal.jpg",
            "Monkey 47 Schwarzwald Dry Gin": "https://upload.wikimedia.org/wikipedia/commons/b/b7/Monkey_47_-_Schwarzwald_Dry_Gin_-_Packshot.jpg",
            "Sipsmith London Dry": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Sipsmith_London_Logo.png",
        }

        # Load the fixture data
        # Use __file__ to get the absolute path of the command file, then go up to project directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        fixture_path = os.path.join(project_root, 'calculator', 'fixtures', 'famous_gin_recipes.json')
        with open(fixture_path, 'r') as f:
            recipes_data = json.load(f)

        created_count = 0
        for recipe_data in recipes_data:
            # Check if recipe already exists -> backfill its image_url, then skip re-create
            existing = GinRecipe.objects.filter(name=recipe_data['name']).first()
            if existing:
                new_url = IMAGE_URLS.get(recipe_data['name'], "")
                if new_url and existing.image_url != new_url:
                    existing.image_url = new_url
                    existing.save(update_fields=['image_url'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated image for existing recipe "{existing.name}".')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Recipe "{recipe_data["name"]}" already exists. Skipping.')
                    )
                continue

            # Create the recipe
            recipe = GinRecipe.objects.create(
                name=recipe_data['name'],
                description=recipe_data['description'],
                base_volume=recipe_data['base_volume'],
                abv_volume=recipe_data['abv_volume'],
                target_abv_percentage=recipe_data['target_abv_percentage'],
                is_active=recipe_data['is_active'],
                is_default=recipe_data['is_default'],
                image_url=IMAGE_URLS.get(recipe_data['name'], ""),
                created_by=admin_user
            )

            # Create the ingredients
            for ingredient_data in recipe_data['ingredients']:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=ingredient_data['name'],
                    amount=ingredient_data['amount'],
                    is_optional=ingredient_data['is_optional'],
                    notes=ingredient_data['notes'],
                    order=ingredient_data['order']
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created recipe "{recipe.name}" with {len(recipe_data["ingredients"])} ingredients.')
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new recipes.')
        )