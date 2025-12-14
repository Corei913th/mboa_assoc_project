"""
Service de gestion des codes OTP (One-Time Password).
Génère, valide et gère l'expiration des codes OTP pour l'authentification par SMS.
"""

import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from mboa_assoc_app.models import OTPCode


class OTPService:
    """
    Service pour gérer les codes OTP.
    Gère la génération, validation et expiration des codes.
    """
    
    @staticmethod
    def generate_otp(telephone: str) -> OTPCode:
        """
        Génère un code OTP à 6 chiffres avec expiration de 10 minutes.
        
        Args:
            telephone: Numéro de téléphone au format +237XXXXXXXXX
            
        Returns:
            OTPCode: Instance du code OTP créé
            
        Requirements: 1.2, 1.3
        """
        # Générer un code à 6 chiffres
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Calculer la date d'expiration (10 minutes)
        expiration_minutes = settings.OTP_EXPIRATION_MINUTES
        expires_at = timezone.now() + timedelta(minutes=expiration_minutes)
        
        # Créer le code OTP
        otp_code = OTPCode.objects.create(
            telephone=telephone,
            code=code,
            expires_at=expires_at
        )
        
        return otp_code
    
    @staticmethod
    def validate_otp(telephone: str, code: str) -> tuple[bool, str]:
        """
        Valide un code OTP pour un numéro de téléphone.
        Vérifie la correspondance du code et l'expiration.
        
        Args:
            telephone: Numéro de téléphone
            code: Code OTP à valider
            
        Returns:
            tuple[bool, str]: (succès, message)
            
        Requirements: 2.1, 2.2, 2.5
        """
        try:
            # Récupérer le dernier code OTP non validé et non expiré pour ce téléphone
            otp_code = OTPCode.objects.filter(
                telephone=telephone,
                is_validated=False,
                is_expired=False
            ).order_by('-created_at').first()
            
            if not otp_code:
                return False, "Aucun code OTP actif trouvé pour ce numéro"
            
            # Vérifier si le code est expiré
            if OTPService.is_expired(otp_code):
                OTPService.invalidate_otp(otp_code)
                return False, "Code expiré. Demandez un nouveau code"
            
            # Vérifier si le nombre maximum de tentatives est atteint
            max_attempts = settings.OTP_MAX_ATTEMPTS
            if otp_code.attempts >= max_attempts:
                OTPService.invalidate_otp(otp_code)
                return False, f"Nombre maximum de tentatives atteint ({max_attempts}). Demandez un nouveau code"
            
            # Incrémenter le compteur de tentatives
            otp_code.attempts += 1
            otp_code.save()
            
            # Vérifier la correspondance du code
            if otp_code.code != code:
                tentatives_restantes = max_attempts - otp_code.attempts
                if tentatives_restantes > 0:
                    return False, f"Code incorrect. {tentatives_restantes} tentative(s) restante(s)"
                else:
                    OTPService.invalidate_otp(otp_code)
                    return False, "Code incorrect. Nombre maximum de tentatives atteint. Demandez un nouveau code"
            
            # Code valide : marquer comme validé
            otp_code.is_validated = True
            otp_code.save()
            
            return True, "Code validé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    @staticmethod
    def is_expired(otp: OTPCode) -> bool:
        """
        Vérifie si un code OTP est expiré.
        
        Args:
            otp: Instance OTPCode à vérifier
            
        Returns:
            bool: True si expiré, False sinon
            
        Requirements: 2.2
        """
        return timezone.now() > otp.expires_at
    
    @staticmethod
    def invalidate_otp(otp: OTPCode) -> None:
        """
        Invalide un code OTP (après expiration ou échecs multiples).
        
        Args:
            otp: Instance OTPCode à invalider
            
        Requirements: 2.5
        """
        otp.is_expired = True
        otp.save()
