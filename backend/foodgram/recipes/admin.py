from django.contrib import admin

from .models import (
    Ingredient,
    Tag,
    Recipe,
    IngredientInRecipe,
    TagInRecipe,
    ShoppingCart,
    Favorite,
)

admin.site.empty_value_display = 'Не задано'

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientInRecipe)
admin.site.register(TagInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
