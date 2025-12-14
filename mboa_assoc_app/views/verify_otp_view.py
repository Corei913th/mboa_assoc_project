"""
Vue de vérification du code OTP.
Gère la validation du code OTP, les tentatives et la création du compte utilisateur.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from mboa_assoc_app.forms import OTPVerificationForm
from mboa_assoc_app.services.otp_service import OTPService
from mboa_assoc_app.services.security_service import SecurityService
from mboa_assoc_app.models import Membre, OTPAttempt

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Récupère l'adresse IP du client depuis la requête.
    Gère les proxies et load balancers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verify_otp_view(request):
    """
    Vue de vérification du code OTP.
    
    Processus:
    1. Récupérer le téléphone depuis la session
    2. Valider le code OTP saisi
    3. Gérer les tentatives (max 3 par code)
    4. Enregistrer les tentatives dans l'historique
    5. Si succès: marquer téléphone comme vérifié et créer le compte
    6. Si échec: incrémenter compteur et gérer blocage si nécessaire
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    # Vérifier que le téléphone est en session (vient de l'inscription)
    telephone = request.session.get('registration_phone')
    
    if not telephone:
        messages.error(
            request,
            "Session expirée. Veuillez recommencer l'inscription."
        )
        logger.warning("Tentative d'accès à verify_otp sans téléphone en session")
        return redirect('register')
    
    # Vérifier si le téléphone est bloqué (Requirement 3.3)
    if SecurityService.check_phone_blocked(telephone):
        messages.error(
            request,
            "Trop de tentatives échouées. Votre numéro est temporairement bloqué. "
            "Veuillez réessayer dans 1 heure."
        )
        logger.warning(f"Tentative de vérification OTP avec numéro bloqué: {telephone}")
        return render(request, 'auth/verify_otp.html', {
            'form': OTPVerificationForm(),
            'telephone': telephone,
            'blocked': True
        })
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        
        if form.is_valid():
            code = form.cleaned_data['code']
            ip_address = get_client_ip(request)
            
            # Valider le code OTP (Requirements 2.1, 2.2)
            success, message = OTPService.validate_otp(telephone, code)
            
            # Récupérer le code OTP pour enregistrer la tentative
            from mboa_assoc_app.models import OTPCode
            otp_code = OTPCode.objects.filter(
                telephone=telephone,
                is_validated=False,
                is_expired=False
            ).order_by('-created_at').first()
            
            # Enregistrer la tentative dans l'historique
            if otp_code:
                OTPAttempt.objects.create(
                    otp_code=otp_code,
                    success=success,
                    ip_address=ip_address
                )
                logger.info(
                    f"Tentative OTP enregistrée pour {telephone}: "
                    f"{'succès' if success else 'échec'} depuis {ip_address}"
                )
            
            if success:
                # Code validé avec succès (Requirement 2.3)
                logger.info(f"Code OTP validé avec succès pour {telephone}")
                
                # Créer le compte utilisateur
                try:
                    # Vérifier si le membre existe déjà
                    membre = Membre.objects.filter(telephone=telephone).first()
                    
                    if not membre:
                        # Créer un nouveau membre
                        password = request.session.get('registration_password')
                        
                        if not password:
                            messages.error(request, "Session expirée. Veuillez recommencer l'inscription.")
                            return redirect('register')
                        
                        # Créer le membre - username = téléphone normalisé
                        membre = Membre.objects.create_user(
                            username=telephone,
                            telephone=telephone,
                            password=password,
                            telephone_verifie=True,
                            date_verification_telephone=timezone.now()
                        )
                        logger.info(f"Nouveau membre créé: {telephone}")
                    else:
                        # Marquer le téléphone comme vérifié (Requirement 2.3)
                        membre.telephone_verifie = True
                        membre.date_verification_telephone = timezone.now()
                        membre.save()
                        logger.info(f"Téléphone vérifié pour membre existant: {membre.username}")
                    
                    # Connecter automatiquement l'utilisateur
                    login(request, membre, backend='mboa_assoc_app.backends.PhoneBackend')
                    
                    # Mettre à jour la dernière connexion
                    membre.derniere_connexion = timezone.now()
                    membre.save()
                    
                    # Nettoyer la session
                    if 'registration_phone' in request.session:
                        del request.session['registration_phone']
                    if 'registration_password' in request.session:
                        del request.session['registration_password']
                    
                    messages.success(
                        request,
                        "Votre téléphone a été vérifié avec succès ! "
                        "Veuillez compléter votre profil."
                    )
                    
                    # Rediriger vers la page de profil pour compléter les informations
                    return redirect('profile')
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création du compte pour {telephone}: {e}")
                    messages.error(
                        request,
                        "Erreur lors de la création du compte. Veuillez réessayer."
                    )
            else:
                # Code invalide ou expiré (Requirement 2.4)
                logger.warning(f"Échec de validation OTP pour {telephone}: {message}")
                
                # Incrémenter le compteur d'échecs pour la sécurité
                SecurityService.increment_failure(telephone)
                
                # Afficher le message d'erreur
                messages.error(request, message)
                
                # Vérifier si le numéro vient d'être bloqué
                if SecurityService.check_phone_blocked(telephone):
                    messages.error(
                        request,
                        "Trop de tentatives échouées. Votre numéro est temporairement bloqué "
                        "pour 1 heure."
                    )
                    return render(request, 'auth/verify_otp.html', {
                        'form': OTPVerificationForm(),
                        'telephone': telephone,
                        'blocked': True
                    })
        else:
            # Erreurs de validation du formulaire
            logger.warning(f"Formulaire de vérification OTP invalide: {form.errors}")
    else:
        form = OTPVerificationForm()
    
    return render(request, 'auth/verify_otp.html', {
        'form': form,
        'telephone': telephone,
        'blocked': False
    })
