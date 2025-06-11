from django.db import models
from django.contrib.auth.models import User


class GinRecipe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    base_volume = models.FloatField(default=1.0, help_text="Base volume in liters")
    abv_volume = models.FloatField(help_text="ABV volume in liters for base volume")
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


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(GinRecipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    amount = models.FloatField(help_text="Amount in grams for base volume")
    is_optional = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['recipe', 'name']

    def __str__(self):
        return f"{self.recipe.name} - {self.name} ({self.amount}g)"
