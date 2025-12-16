"""
Vue de gestion du profil utilisateur.
Permet aux membres de consulter et modifier leurs informations personnelles.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mboa_assoc_app.forms import ProfileForm

logger = logging.getLogger(__name__)


@login_required
def profile_view(request):
    """
    Vue de gestion du profil utilisateur.
    
    Processus:
    1. Afficher le formulaire de profil avec les données actuelles
    2. Valider les modifications soumises
    3. Valider le format et la taille de la photo (JPEG/PNG, max 5MB)
    4. Sauvegarder les modifications en base de données
    5. Afficher un message de confirmation
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            try:
                # Sauvegarder les modifications (Requirement 5.5)
                membre = form.save()
                
                messages.success(
                    request,
                    "Votre profil a été mis à jour avec succès."
                )
                logger.info(f"Profil mis à jour pour l'utilisateur {membre.username}")
                
                # Rediriger vers la même page pour afficher les modifications
                return redirect('mboa_assoc_app:profile')
                
            except Exception as e:
                # Gestion des erreurs système
                logger.error(f"Erreur lors de la mise à jour du profil pour {request.user.username}: {e}")
                messages.error(
                    request,
                    "Une erreur s'est produite lors de la mise à jour de votre profil. Veuillez réessayer."
                )
        else:
            # Erreurs de validation du formulaire
            logger.warning(f"Formulaire de profil invalide pour {request.user.username}: {form.errors}")
            
            # Afficher les erreurs spécifiques pour la photo (Requirements 5.2)
            if 'photo_profil' in form.errors:
                for error in form.errors['photo_profil']:
                    messages.error(request, error)
    else:
        # Afficher le formulaire avec les données actuelles (Requirement 5.1)
        form = ProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'membre': request.user
    }
    
    return render(request, 'auth/profile.html', context)
