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
                    'water_for_maceration': recipe.water_for_maceration,
                    'ingredients': ingredients
                }
            })
            
        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': 'Invalid input data'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
