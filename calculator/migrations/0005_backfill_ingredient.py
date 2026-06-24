from django.db import migrations


def backfill_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('calculator', 'Ingredient')
    RecipeIngredient = apps.get_model('calculator', 'RecipeIngredient')

    for ri in RecipeIngredient.objects.all():
        clean_name = ri.name.strip()
        ingredient = Ingredient.objects.filter(name__iexact=clean_name).first()
        if ingredient is None:
            ingredient = Ingredient.objects.create(name=clean_name)
        ri.ingredient = ingredient
        ri.save(update_fields=['ingredient'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_ingredient'),
    ]

    operations = [
        migrations.RunPython(backfill_ingredients, noop_reverse),
    ]
