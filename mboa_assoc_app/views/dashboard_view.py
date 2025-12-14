"""
Vue du tableau de bord principal.
Affiche un résumé des informations de l'utilisateur connecté.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Vue du tableau de bord principal.
    Accessible uniquement aux utilisateurs connectés.
    """
    return render(request, 'dashboard.html', {
        'user': request.user
    })
