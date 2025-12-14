"""
Vue de déconnexion.
Gère la destruction de la session et la redirection vers la page de connexion.
"""

import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

logger = logging.getLogger(__name__)


def logout_view(request):
    """
    Vue de déconnexion.
    
    Processus:
    1. Détruire la session utilisateur
    2. Afficher un message de confirmation
    3. Rediriger vers la page de connexion
    
    Requirements: 4.5
    """
    if request.user.is_authenticated:
        username = request.user.username
        
        # Détruire la session (Requirement 4.5)
        logout(request)
        
        logger.info(f"Déconnexion réussie pour {username}")
        
        messages.success(
            request,
            "Vous avez été déconnecté avec succès."
        )
    
    # Rediriger vers page de connexion (Requirement 4.5)
    return redirect('login')
