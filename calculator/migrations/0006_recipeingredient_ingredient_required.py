import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0005_backfill_ingredient'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='recipeingredient',
            name='name',
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recipe_ingredients', to='calculator.ingredient'),
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'ordering': ['order', 'ingredient__name']},
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together={('recipe', 'ingredient')},
        ),
    ]
