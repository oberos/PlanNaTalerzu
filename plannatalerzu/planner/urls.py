from django.urls import path

from .views import planner_index

app_name = "planner"

urlpatterns = [
    path("", planner_index, name="index"),
]
