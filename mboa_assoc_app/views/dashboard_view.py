"""
Vue du tableau de bord principal.
Affiche un résumé des informations de l'utilisateur connecté.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Adhesion, Invitation


@login_required
def dashboard_view(request):
    """
    Vue du tableau de bord principal.
    Accessible uniquement aux utilisateurs connectés.
    """
    # Récupérer les associations de l'utilisateur
    associations = Adhesion.objects.filter(
        membre=request.user,
        is_active=True
    ).select_related('association').order_by('-date')
    
    # Récupérer les invitations en attente
    invitations_en_attente = Invitation.objects.filter(
        telephone_invite=request.user.telephone,
        statut=Invitation.StatutInvitation.EN_ATTENTE
    ).count()
    
    return render(request, 'dashboard.html', {
        'user': request.user,
        'associations': associations,
        'invitations_count': invitations_en_attente
    })
