from django.test import TestCase, Client
from django.urls import reverse
from calculator.models import GinRecipe, RecipeIngredient
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
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            name=" juniper berries",
            amount=20.0,
            is_optional=False,
            notes=""
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            name="coriander seeds",
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

    def test_calculate_endpoint(self):
        """Test the calculate endpoint"""
        client = Client()
        
        # Calculate with recipe id=1 (Classic London Dry), volume 1 liter, 96% spirit, target 40%
        response = client.post(
            reverse('calculate'),
            data={
                'volume': 1.0,
                'recipe_id': 1,
                'input_spirit_abv': 96.0,
                'target_abv': 40.0
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['recipe_name'], 'Classic London Dry')
        # Verify correct calculation: with 1L volume, 96% spirit, 40% target
        # spirit_needed = (1 * 40 / 100) / (96 / 100) = 0.42 L
        # water_to_add = 1 - 0.42 = 0.58 L
        self.assertAlmostEqual(data['spirit_needed'], 0.42, places=2)
        self.assertAlmostEqual(data['water_to_add'], 0.58, places=2)
        
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
