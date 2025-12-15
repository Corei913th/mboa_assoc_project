from django.shortcuts import render


def landing_view(request):
    """
    Vue pour la page d'accueil (landing page)
    """
    return render(request, 'landing.html')
