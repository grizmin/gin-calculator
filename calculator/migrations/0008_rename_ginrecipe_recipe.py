from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('calculator', '0007_ginrecipe_water_for_maceration')]
    operations = [migrations.RenameModel('GinRecipe', 'Recipe')]
