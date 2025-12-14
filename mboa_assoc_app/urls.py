# URLs pour la gestion des associations
from django.urls import path, include

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
]