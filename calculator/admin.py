from django.contrib import admin
from .models import GinRecipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ['name', 'amount', 'is_optional', 'notes', 'order']
    ordering = ['order', 'name']


@admin.register(GinRecipe)
class GinRecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_volume', 'abv_volume', 'is_active', 'is_default', 'created_by', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RecipeIngredientInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Recipe Details', {
            'fields': ('base_volume', 'abv_volume')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_default')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'name', 'amount', 'is_optional', 'order']
    list_filter = ['recipe', 'is_optional']
    search_fields = ['name', 'recipe__name']
    ordering = ['recipe', 'order', 'name']
