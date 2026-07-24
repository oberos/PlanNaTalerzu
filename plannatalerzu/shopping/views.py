from django.shortcuts import render


def shopping_index(request):
    return render(request, "shopping/index.html", {"page_title": "Lista zakupów"})
