from django.urls import path

from .views import shopping_index

app_name = "shopping"

urlpatterns = [
    path("", shopping_index, name="index"),
]
