from django.urls import path

from .views import import_confirm, import_preview, ingredient_index, recipe_index

app_name = "recipes"

urlpatterns = [
    path("", recipe_index, name="index"),
    path("ingredients/", ingredient_index, name="ingredients"),
    path("import/preview/", import_preview, name="import_preview"),
    path("import/confirm/", import_confirm, name="import_confirm"),
]
