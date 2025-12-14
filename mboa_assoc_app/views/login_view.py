"""
Vue de connexion avec téléphone et mot de passe.
Gère l'authentification, la création de session et la mise à jour de derniere_connexion.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils import timezone
from mboa_assoc_app.forms import LoginForm

logger = logging.getLogger(__name__)


def login_view(request):
    """
    Vue de connexion avec téléphone et mot de passe.
    
    Processus:
    1. Valider le format du téléphone et le mot de passe
    2. Authentifier les identifiants avec Django
    3. Créer une session utilisateur si authentification réussie
    4. Mettre à jour la date de dernière connexion
    5. Rediriger vers le dashboard
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    # Rediriger si déjà connecté
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            telephone = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authentifier avec téléphone + mot de passe (Requirement 4.1)
            user = authenticate(request, username=telephone, password=password)
            
            if user is not None:
                # Créer session Django (Requirement 4.2)
                login(request, user)
                
                # Mettre à jour derniere_connexion (Requirement 4.4)
                user.derniere_connexion = timezone.now()
                user.save(update_fields=['derniere_connexion'])
                
                logger.info(f"Connexion réussie pour {telephone}")
                
                messages.success(
                    request,
                    f"Bienvenue {user.get_full_name() or user.username} !"
                )
                
                # Rediriger vers la page demandée ou le dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                # Identifiants invalides (Requirement 4.3)
                messages.error(
                    request,
                    "Numéro de téléphone ou mot de passe incorrect."
                )
                logger.warning(f"Tentative de connexion échouée pour {telephone}")
        else:
            # Erreurs de validation du formulaire
            logger.warning(f"Formulaire de connexion invalide: {form.errors}")
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})
