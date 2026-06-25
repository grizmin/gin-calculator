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
            description="A traditional London dry gin with classic botanicals",
            image_url="https://example.com/classic.jpg",
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
            notes="Primary botanical"
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            ingredient=coriander,
            amount=10.0,
            is_optional=False,
            notes="Secondary botanical"
        )

    def test_get_recipe_endpoint(self):
        """Test the get_recipe endpoint returns all expected fields"""
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
        
        # Verify recipe structure
        recipe = data['recipe']
        self.assertEqual(recipe['name'], 'Classic London Dry')
        self.assertEqual(recipe['target_abv_percentage'], 40.0)
        
        # Verify all expected response fields are present (including new ones)
        expected_fields = ['id', 'name', 'description', 'image_url', 'base_volume', 
                          'abv_volume', 'target_abv_percentage', 'ingredients']
        for field in expected_fields:
            self.assertIn(field, recipe, f"Missing field '{field}' in recipe response")
        
        # Verify field values
        self.assertEqual(recipe['description'], "A traditional London dry gin with classic botanicals")
        self.assertEqual(recipe['image_url'], "https://example.com/classic.jpg")
        self.assertEqual(recipe['base_volume'], 1.0)
        self.assertEqual(recipe['abv_volume'], 0.4)
        
        # Verify ingredients are present
        self.assertIsInstance(recipe['ingredients'], list)
        self.assertEqual(len(recipe['ingredients']), 2)
        
        # Verify ingredient structure with new Ingredient model
        for ingredient in recipe['ingredients']:
            self.assertIn('name', ingredient)
            self.assertIn('amount', ingredient)
            self.assertIn('is_optional', ingredient)
            self.assertIn('notes', ingredient)

    def test_calculate_endpoint(self):
        """Test the calculate endpoint returns all expected fields"""
        client = Client()
        
        # Calculate with recipe id=1 (Classic London Dry), volume 1 liter, 96% spirit, target 40%
        response = client.post(
            reverse('calculate'),
            data={
                'volume': 1.0,
                'recipe_id': 1,
                'input_spirit_abv': 96.0,
                'target_abv': 40.0,
                'still_yield': 85.0
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify recipe name and description are in response
        self.assertEqual(data['recipe_name'], 'Classic London Dry')
        self.assertIn('recipe_description', data)
        
        # Verify correct calculation: with 1L volume, 96% spirit, 40% target
        # spirit_needed = (1 * 40 / 100) / (96 / 100) = 0.42 L
        # water_to_add = 1 - 0.42 = 0.58 L
        self.assertAlmostEqual(data['spirit_needed'], 0.42, places=2)
        self.assertAlmostEqual(data['water_to_add'], 0.58, places=2)
        
        # Verify all expected response fields are present (including new ones)
        expected_fields = ['success', 'recipe_name', 'recipe_description', 'scaled_ingredients',
                          'abv_volume', 'scale_factor', 'spirit_needed', 'water_to_add', 'spirit_to_load']
        for field in expected_fields:
            self.assertIn(field, data, f"Missing field '{field}' in calculate response")
        
        # Verify scaled_ingredients structure with new base_amount field
        self.assertIsInstance(data['scaled_ingredients'], list)
        self.assertEqual(len(data['scaled_ingredients']), 2)
        
        for ingredient in data['scaled_ingredients']:
            self.assertIn('name', ingredient)
            self.assertIn('amount', ingredient)
            self.assertIn('base_amount', ingredient)  # NEW field
            self.assertIn('is_optional', ingredient)
            self.assertIn('notes', ingredient)
        
        # Verify scaling calculation (2x volume should double ingredients)
        self.assertEqual(data['scale_factor'], 1.0)
        
    def test_calculate_with_scaled_volume(self):
        """Test calculate endpoint with scaled volume"""
        client = Client()
        
        # Calculate with 2x volume
        response = client.post(
            reverse('calculate'),
            data={
                'volume': 2.0,
                'recipe_id': 1,
                'input_spirit_abv': 96.0,
                'target_abv': 40.0
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify scale factor
        self.assertEqual(data['scale_factor'], 2.0)
        
        # Verify ingredients are scaled correctly
        for ingredient in data['scaled_ingredients']:
            # Base amount should match original recipe ingredient amounts
            # Scaled amount should be base_amount * scale_factor
            expected_scaled = round(ingredient['base_amount'] * 2.0, 2)
            self.assertEqual(ingredient['amount'], expected_scaled)
        
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

    def test_ingredient_model_relationship(self):
        """Test that RecipeIngredient correctly references Ingredient via FK"""
        # Verify that the test setup correctly uses the Ingredient model
        recipe = GinRecipe.objects.get(id=self.recipe1.id)
        recipe_ingredients = recipe.ingredients.all()
        
        self.assertEqual(recipe_ingredients.count(), 2)
        
        # Verify each RecipeIngredient has a proper ingredient FK reference
        for ri in recipe_ingredients:
            self.assertIsNotNone(ri.ingredient)
            self.assertEqual(ri.ingredient.name, ri.ingredient.name)  # Ingredient has name
            self.assertIn(ri.ingredient.name, ['Juniper Berries', 'Coriander Seeds'])
            self.assertTrue(ri.amount > 0)

    def test_invalid_recipe_id(self):
        """Test handling of invalid recipe_id"""
        client = Client()
        
        response = client.post(
            reverse('get_recipe'),
            data={'recipe_id': 99999},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)


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
