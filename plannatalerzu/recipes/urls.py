from django.urls import path

from .views import recipe_index

app_name = "recipes"

urlpatterns = [
    path("", recipe_index, name="index"),
]
