from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GinRecipe, RecipeIngredient
import json


def index(request):
    """Main calculator page"""
    # Get all active recipes
    recipes = GinRecipe.objects.filter(is_active=True).prefetch_related('ingredients__ingredient')
    
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
            for ri in recipe.ingredients.select_related('ingredient').all():
                scaled_amount = round(ri.amount * scale_factor, 2)
                scaled_ingredients.append({
                    'name': ri.ingredient.name,
                    'amount': scaled_amount,
                    'base_amount': ri.amount,
                    'is_optional': ri.is_optional,
                    'notes': ri.notes
                })
            
            # Calculate scaled ABV volume
            scaled_abv_volume = round(recipe.abv_volume * scale_factor, 2)
            
            # Calculate spirit needed and water to add
            # The calculation:
            # Spirit needed = (desired_volume * target_abv_percentage) / 100 / (input_spirit_abv / 100)
            # Water to add = desired_volume - spirit_needed
            # Note: Water amount is estimated since distillation output varies per brew
            input_spirit_abv = float(data.get('input_spirit_abv', 40.0))  # Default to 40% if not provided
            target_abv_percentage = float(data.get('target_abv', recipe.target_abv_percentage or 40.0))
            
            # FIXED: Corrected formula - input_spirit_abv is percentage (e.g. 96), not decimal (0.96)
            spirit_needed = (desired_volume * target_abv_percentage / 100) / (input_spirit_abv / 100)
            water_to_add = desired_volume - spirit_needed

            still_yield = float(data.get('still_yield', 100.0))
            spirit_to_load = round(spirit_needed / (still_yield / 100), 2)

            return JsonResponse({
                'success': True,
                'recipe_name': recipe.name,
                'recipe_description': recipe.description,
                'scaled_ingredients': scaled_ingredients,
                'abv_volume': scaled_abv_volume,
                'scale_factor': round(scale_factor, 2),
                'spirit_needed': round(spirit_needed, 2),
                'water_to_add': round(water_to_add, 2),
                'spirit_to_load': spirit_to_load,
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
            for ri in recipe.ingredients.select_related('ingredient').all():
                ingredients.append({
                    'name': ri.ingredient.name,
                    'amount': ri.amount,
                    'is_optional': ri.is_optional,
                    'notes': ri.notes
                })
            
            return JsonResponse({
                'success': True,
                'recipe': {
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'image_url': recipe.image_url,
                    'base_volume': recipe.base_volume,
                    'abv_volume': recipe.abv_volume,
                    'target_abv_percentage': recipe.target_abv_percentage,
                    'ingredients': ingredients
                }
            })
            
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid input data'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
