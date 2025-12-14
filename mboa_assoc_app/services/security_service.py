"""
Service de sécurité pour la gestion des blocages de téléphone.
Gère les tentatives échouées et les blocages temporaires pour prévenir les attaques par force brute.
"""

from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from mboa_assoc_app.models import PhoneBlock, OTPAttempt
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """
    Service de sécurité pour gérer les blocages de numéros de téléphone.
    Implémente les mécanismes anti-abus pour l'authentification OTP.
    """
    
    @staticmethod
    def check_phone_blocked(telephone: str) -> bool:
        """
        Vérifie si un numéro de téléphone est actuellement bloqué.
        
        Args:
            telephone: Numéro de téléphone au format +237XXXXXXXXX
            
        Returns:
            bool: True si le téléphone est bloqué, False sinon
        """
        try:
            # Chercher un blocage actif pour ce numéro
            block = PhoneBlock.objects.filter(telephone=telephone).first()
            
            if not block:
                return False
            
            # Vérifier si le blocage est encore actif
            now = timezone.now()
            if now < block.blocked_until:
                logger.info(f"Téléphone {telephone} est bloqué jusqu'à {block.blocked_until}")
                return True
            else:
                # Le blocage a expiré, on peut le supprimer
                logger.info(f"Blocage expiré pour {telephone}, suppression")
                block.delete()
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du blocage pour {telephone}: {e}")
            # En cas d'erreur, on considère que le téléphone n'est pas bloqué
            # pour ne pas bloquer l'utilisateur de manière permanente
            return False
    
    @staticmethod
    def increment_failure(telephone: str) -> None:
        """
        Incrémente le compteur d'échecs pour un numéro de téléphone.
        Bloque automatiquement le numéro si le nombre maximum d'échecs est atteint.
        
        Args:
            telephone: Numéro de téléphone au format +237XXXXXXXXX
        """
        try:
            # Compter le nombre total d'échecs récents (dernières 24h)
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            
            # Compter les tentatives échouées pour ce téléphone
            failed_attempts = OTPAttempt.objects.filter(
                otp_code__telephone=telephone,
                success=False,
                attempted_at__gte=twenty_four_hours_ago
            ).count()
            
            logger.info(f"Téléphone {telephone} a {failed_attempts} échecs dans les dernières 24h")
            
            # Vérifier si on doit bloquer le numéro
            max_failures = settings.PHONE_MAX_FAILURES
            if failed_attempts >= max_failures:
                logger.warning(f"Nombre maximum d'échecs atteint pour {telephone}, blocage du numéro")
                SecurityService.block_phone(
                    telephone=telephone,
                    duration_hours=settings.PHONE_BLOCK_DURATION_HOURS
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de l'incrémentation des échecs pour {telephone}: {e}")
    
    @staticmethod
    def block_phone(telephone: str, duration_hours: int) -> None:
        """
        Bloque un numéro de téléphone pour une durée spécifiée.
        
        Args:
            telephone: Numéro de téléphone au format +237XXXXXXXXX
            duration_hours: Durée du blocage en heures
        """
        try:
            now = timezone.now()
            blocked_until = now + timedelta(hours=duration_hours)
            
            # Compter le nombre total d'échecs récents
            twenty_four_hours_ago = now - timedelta(hours=24)
            total_failures = OTPAttempt.objects.filter(
                otp_code__telephone=telephone,
                success=False,
                attempted_at__gte=twenty_four_hours_ago
            ).count()
            
            # Créer ou mettre à jour le blocage
            block, created = PhoneBlock.objects.update_or_create(
                telephone=telephone,
                defaults={
                    'blocked_until': blocked_until,
                    'total_failures': total_failures,
                    'reason': f"Trop de tentatives échouées ({total_failures} échecs)"
                }
            )
            
            action = "créé" if created else "mis à jour"
            logger.warning(
                f"Blocage {action} pour {telephone} jusqu'à {blocked_until} "
                f"({total_failures} échecs)"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du blocage de {telephone}: {e}")
    
    @staticmethod
    def unblock_expired() -> int:
        """
        Débloque automatiquement tous les numéros dont la période de blocage a expiré.
        Cette fonction devrait être appelée périodiquement (par exemple via une tâche cron).
        
        Returns:
            int: Nombre de numéros débloqués
        """
        try:
            now = timezone.now()
            
            # Trouver tous les blocages expirés
            expired_blocks = PhoneBlock.objects.filter(blocked_until__lte=now)
            count = expired_blocks.count()
            
            if count > 0:
                # Supprimer les blocages expirés
                expired_blocks.delete()
                logger.info(f"{count} numéro(s) débloqué(s) automatiquement")
            
            return count
            
        except Exception as e:
            logger.error(f"Erreur lors du déblocage automatique: {e}")
            return 0
