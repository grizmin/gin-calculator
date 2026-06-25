from django.test import TestCase, Client
from django.urls import reverse
from calculator.models import GinRecipe, RecipeIngredient, Ingredient
from django.contrib.auth.models import User

class CalculatorViewsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test recipes
        self.recipe1 = GinRecipe.objects.create(
            name="Classic London Dry",
            base_volume=1.0,
            abv_volume=0.4,
            target_abv_percentage=40.0,
            is_active=True,
            is_default=True,
            created_by=self.user
        )
        
        # Add ingredients to recipe 1
        juniper = Ingredient.objects.get_or_create(name="Juniper Berries")[0]
        coriander = Ingredient.objects.get_or_create(name="Coriander Seeds")[0]
        
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            ingredient=juniper,
            amount=20.0,
            is_optional=False,
            notes=""
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            ingredient=coriander,
            amount=10.0,
            is_optional=False,
            notes=""
        )

    def test_get_recipe_endpoint(self):
        """Test the get_recipe endpoint"""
        client = Client()
        
        # Get the default recipe (id=1)
        response = client.post(
            reverse('get_recipe'),
            data={'recipe_id': 1},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['recipe']['name'], 'Classic London Dry')
        self.assertEqual(data['recipe']['target_abv_percentage'], 40.0)
        self.assertEqual(data['recipe']['water_for_maceration'], 0.0)

 
        
    def test_target_abv_prefills_from_recipe(self):
        """Test that target_abv input field correctly prefills from recipe"""
        client = Client()
        
        # Test loading a recipe to check if target_abv is properly set
        response = client.post(
            reverse('get_recipe'),
            data={'recipe_id': 1},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('recipe', data)
        self.assertEqual(data['recipe']['target_abv_percentage'], 40.0)


class FamousRecipesCommandTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

    def test_creates_all_8_recipes(self):
        """Test that the command creates all 8 recipes"""
        # Delete any existing famous recipes
        GinRecipe.objects.filter(
            name__in=[
                'Tanqueray London Dry',
                "Hendrick's",
                'Bombay Sapphire',
                'Beefeater London Dry',
                'Aviation American Gin',
                "Gordon's London Dry",
                'Monkey 47 Schwarzwald Dry Gin',
                'Sipsmith London Dry'
            ]
        ).delete()
        
        # Run the command by calling it directly
        from django.core.management import call_command
        call_command('create_famous_recipes')
        
        # Verify 8 recipes exist
        famous_recipes = GinRecipe.objects.filter(
            name__in=[
                'Tanqueray London Dry',
                "Hendrick's",
                'Bombay Sapphire',
                'Beefeater London Dry',
                'Aviation American Gin',
                "Gordon's London Dry",
                'Monkey 47 Schwarzwald Dry Gin',
                'Sipsmith London Dry'
            ]
        )
        self.assertEqual(famous_recipes.count(), 8)

    def test_idempotent(self):
        """Test that running the command twice doesn't create duplicates"""
        from django.core.management import call_command
        
        # Run command twice
        call_command('create_famous_recipes')
        count_after_first = GinRecipe.objects.filter(name='Tanqueray London Dry').count()
        
        call_command('create_famous_recipes')
        count_after_second = GinRecipe.objects.filter(name='Tanqueray London Dry').count()
        
        # Should still be 1, not 2
        self.assertEqual(count_after_first, 1)
        self.assertEqual(count_after_second, 1)

    def test_tanqueray_has_4_ingredients(self):
        """Test that Tanqueray has exactly 4 ingredients"""
        from django.core.management import call_command
        call_command('create_famous_recipes')
        
        tanqueray = GinRecipe.objects.get(name='Tanqueray London Dry')
        self.assertEqual(tanqueray.ingredients.count(), 4)

    def test_monkey47_has_47_ingredients(self):
        """Test that Monkey 47 has exactly 47 ingredients"""
        from django.core.management import call_command
        call_command('create_famous_recipes')
        
        monkey47 = GinRecipe.objects.get(name='Monkey 47 Schwarzwald Dry Gin')
        self.assertEqual(monkey47.ingredients.count(), 47)

    def test_abv_volume_derived_correctly(self):
        """Test that abv_volume is correctly derived from base_volume and target_abv_percentage"""
        from django.core.management import call_command
        call_command('create_famous_recipes')
        
        recipes = GinRecipe.objects.filter(
            name__in=[
                'Tanqueray London Dry',
                "Hendrick's",
                'Bombay Sapphire',
                'Beefeater London Dry',
                'Aviation American Gin',
                "Gordon's London Dry",
                'Monkey 47 Schwarzwald Dry Gin',
                'Sipsmith London Dry'
            ]
        )
        
        for recipe in recipes:
            expected_abv_volume = recipe.base_volume * (recipe.target_abv_percentage / 100)
            self.assertAlmostEqual(
                recipe.abv_volume,
                expected_abv_volume,
                places=3,
                msg=f"{recipe.name}: abv_volume mismatch"
            )

    def test_recipes_have_description_notes(self):
        """Test that all seeded recipes have descriptions with distilling process info"""
        from django.core.management import call_command
        call_command('create_famous_recipes')

        for recipe in GinRecipe.objects.all():
            self.assertTrue(recipe.description)
            self.assertIn("distill", recipe.description.lower())

    def test_ingredients_have_variation_notes(self):
        """Test that all seeded ingredients have non-blank notes"""
        from django.core.management import call_command
        call_command('create_famous_recipes')

        for recipe in GinRecipe.objects.all():
            for ri in recipe.ingredients.all():
                self.assertTrue(ri.notes.strip(), f"{recipe.name}/{ri.ingredient.name}: blank notes")
