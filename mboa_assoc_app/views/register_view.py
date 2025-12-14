"""
Vue d'inscription avec numéro de téléphone.
Gère la validation du téléphone, la génération d'OTP et l'envoi de SMS.
"""

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from mboa_assoc_app.forms import PhoneRegistrationForm
from mboa_assoc_app.services.otp_service import OTPService
from mboa_assoc_app.services.twilio_service import twilio_service
from mboa_assoc_app.services.security_service import SecurityService

logger = logging.getLogger(__name__)


def register_view(request):
    """
    Vue d'inscription avec numéro de téléphone.
    
    Processus:
    1. Valider le format du téléphone (+237XXXXXXXXX)
    2. Vérifier que le téléphone n'est pas bloqué
    3. Générer un code OTP à 6 chiffres
    4. Envoyer le code par SMS via Twilio
    5. Rediriger vers la page de vérification OTP
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    if request.method == 'POST':
        form = PhoneRegistrationForm(request.POST)
        
        if form.is_valid():
            telephone = form.cleaned_data['telephone']
            
            # Vérifier si le téléphone est bloqué (Requirement 3.3)
            if SecurityService.check_phone_blocked(telephone):
                messages.error(
                    request,
                    "Trop de tentatives échouées. Votre numéro est temporairement bloqué. "
                    "Veuillez réessayer dans 1 heure."
                )
                logger.warning(f"Tentative d'inscription avec numéro bloqué: {telephone}")
                return render(request, 'auth/register.html', {'form': form})
            
            try:
                # Générer le code OTP (Requirements 1.2, 1.3)
                otp_code = OTPService.generate_otp(telephone)
                logger.info(f"Code OTP généré pour {telephone}: {otp_code.code}")
                
                # Envoyer le SMS via Twilio (Requirement 1.4)
                message = f"Votre code de vérification est: {otp_code.code}. Valide pendant 10 minutes."
                sms_sent = twilio_service.send_sms(telephone, message)
                
                if sms_sent:
                    # Enregistrer la date d'envoi (Requirement 6.4)
                    otp_code.date_envoi = timezone.now()
                    otp_code.save()
                    
                    # Stocker le téléphone et le mot de passe en session pour la page de vérification
                    request.session['registration_phone'] = telephone
                    request.session['registration_password'] = form.cleaned_data['password']
                    
                    messages.success(
                        request,
                        f"Un code de vérification a été envoyé au {telephone}. "
                        "Veuillez le saisir pour continuer."
                    )
                    logger.info(f"SMS OTP envoyé avec succès à {telephone}")
                    
                    # Rediriger vers la page de vérification OTP (Requirement 1.5)
                    return redirect('verify_otp')
                else:
                    # Échec de l'envoi SMS (Requirement 6.3)
                    messages.error(
                        request,
                        "Erreur lors de l'envoi du SMS. Veuillez réessayer."
                    )
                    logger.error(f"Échec de l'envoi du SMS OTP à {telephone}")
                    
            except Exception as e:
                # Gestion des erreurs système (Design: Error Handling)
                logger.error(f"Erreur lors de l'inscription pour {telephone}: {e}")
                messages.error(
                    request,
                    "Une erreur s'est produite. Veuillez réessayer."
                )
        else:
            # Erreurs de validation du formulaire (Requirement 1.1)
            logger.warning(f"Formulaire d'inscription invalide: {form.errors}")
    else:
        form = PhoneRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})
