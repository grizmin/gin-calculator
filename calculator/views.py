from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GinRecipe, RecipeIngredient
import json


def index(request):
    """Main calculator page"""
    # Get all active recipes
    recipes = GinRecipe.objects.filter(is_active=True).prefetch_related('ingredients')
    
    # Get default recipe or first available
    default_recipe = GinRecipe.objects.filter(is_default=True, is_active=True).first()
    if not default_recipe and recipes.exists():
        default_recipe = recipes.first()
    
    return render(request, 'calculator/index.html', {
        'recipes': recipes,
        'default_recipe': default_recipe,
    })


@csrf_exempt
def calculate(request):
    """Calculate scaled ingredients based on desired volume"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            desired_volume = float(data.get('volume', 1.0))
            recipe_id = data.get('recipe_id')
            
            # Get the selected recipe
            try:
                recipe = GinRecipe.objects.get(id=recipe_id, is_active=True)
            except GinRecipe.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Recipe not found'
                })
            
            # Calculate scaling factor
            scale_factor = desired_volume / recipe.base_volume
            
            # Scale all ingredients
            scaled_ingredients = []
            for ingredient in recipe.ingredients.all():
                scaled_amount = round(ingredient.amount * scale_factor, 2)
                scaled_ingredients.append({
                    'name': ingredient.name,
                    'amount': scaled_amount,
                    'is_optional': ingredient.is_optional,
                    'notes': ingredient.notes
                })
            
            # Calculate scaled ABV volume
            scaled_abv_volume = round(recipe.abv_volume * scale_factor, 2)
            
            return JsonResponse({
                'success': True,
                'recipe_name': recipe.name,
                'recipe_description': recipe.description,
                'scaled_ingredients': scaled_ingredients,
                'abv_volume': scaled_abv_volume,
                'scale_factor': round(scale_factor, 2),
            })
            
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid input data'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_recipe(request):
    """Get recipe details for the frontend"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipe_id = data.get('recipe_id')
            
            try:
                recipe = GinRecipe.objects.get(id=recipe_id, is_active=True)
            except GinRecipe.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Recipe not found'
                })
            
            ingredients = []
            for ingredient in recipe.ingredients.all():
                ingredients.append({
                    'name': ingredient.name,
                    'amount': ingredient.amount,
                    'is_optional': ingredient.is_optional,
                    'notes': ingredient.notes
                })
            
            return JsonResponse({
                'success': True,
                'recipe': {
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'base_volume': recipe.base_volume,
                    'abv_volume': recipe.abv_volume,
                    'ingredients': ingredients
                }
            })
            
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid input data'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
