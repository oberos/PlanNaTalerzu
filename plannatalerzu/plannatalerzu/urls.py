from django.contrib import admin
from django.urls import include, path

from .views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("recipes/", include("recipes.urls")),
    path("planner/", include("planner.urls")),
    path("shopping/", include("shopping.urls")),
]
