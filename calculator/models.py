from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class GinRecipe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, default="", help_text="External image URL for this recipe")
    base_volume = models.FloatField(default=1.0, help_text="Base volume in liters")
    abv_volume = models.FloatField(help_text="ABV volume in liters for base volume")
    target_abv_percentage = models.FloatField(
        default=40.0,
        validators=[MinValueValidator(10.0), MaxValueValidator(99.0)],
        help_text="Target ABV % of the finished gin (10–99%)"
    )
    water_for_maceration = models.FloatField(
        default=0.0,
        help_text="Water needed for maceration in liters"
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one default recipe
        if self.is_default:
            GinRecipe.objects.filter(is_default=True).update(is_default=False)
        
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(GinRecipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='recipe_ingredients')
    amount = models.FloatField(help_text="Amount in grams for base volume")
    is_optional = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'ingredient__name']
        unique_together = ['recipe', 'ingredient']

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name} ({self.amount}g)"
