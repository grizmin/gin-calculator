from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GinRecipe, RecipeIngredient
from .translations import TRANSLATIONS, INGREDIENT_NAMES_BG
import json

_INGREDIENT_NAMES_BG_NORM = {k.lower(): v for k, v in INGREDIENT_NAMES_BG.items()}


def get_ingredient_name_bg(name_en):
    return INGREDIENT_NAMES_BG.get(name_en) or _INGREDIENT_NAMES_BG_NORM.get(name_en.lower()) or name_en


def detect_lang(request):
    """Detect language: cookie > Accept-Language header > 'en'"""
    cookie_lang = request.COOKIES.get('django_language')
    if cookie_lang in TRANSLATIONS:
        return cookie_lang
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept:
        first = accept.split(',')[0].split(';')[0].strip().lower()
        if first.startswith('bg'):
            return 'bg'
    return 'en'


def index(request):
    """Main calculator page"""
    lang = detect_lang(request)
    t = TRANSLATIONS[lang]

    recipes = GinRecipe.objects.filter(is_active=True).prefetch_related('ingredients__ingredient')
    default_recipe = GinRecipe.objects.filter(is_default=True, is_active=True).first()
    if not default_recipe and recipes.exists():
        default_recipe = recipes.first()

    response = render(request, 'calculator/index.html', {
        'recipes': recipes,
        'default_recipe': default_recipe,
        'lang': lang,
        't': t,
    })
    response.set_cookie('django_language', lang, max_age=365*24*60*60)
    return response


@csrf_exempt
def get_recipe(request):
    """Get recipe details for the frontend"""
    lang = detect_lang(request)
    t = TRANSLATIONS[lang]

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipe_id = data.get('recipe_id')
            
            try:
                recipe = GinRecipe.objects.get(id=recipe_id, is_active=True)
            except GinRecipe.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': t['error_recipe_not_found']
                })
            
            ingredients = []
            for ri in recipe.ingredients.select_related('ingredient').all():
                name_en = ri.ingredient.name
                ingredients.append({
                    'name': name_en,
                    'name_bg': get_ingredient_name_bg(name_en),
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
                'error': t['error_invalid_input']
            })
    
    return JsonResponse({'success': False, 'error': t['error_invalid_method']})
