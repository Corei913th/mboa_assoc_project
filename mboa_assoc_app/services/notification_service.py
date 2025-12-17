# Service de notifications (SMS, Email)
# services/notification_service.py
from ..models import Notification, Membre, TypeNotification

class NotificationService:
    
    @staticmethod
    def notifier_invitation(invitation):
        """
        Crée une notification pour une invitation
        """
        try:
            # Chercher le membre invité
            membre_invite = Membre.objects.get(telephone=invitation.telephone_invite)
            
            Notification.objects.create(
                membre=membre_invite,
                type_notification=TypeNotification.NOUVEAU_MEMBRE,
                titre="Nouvelle invitation",
                message=f"{invitation.createur.get_full_name()} vous a invité à rejoindre l'association {invitation.association.name}"
            )
            
        except Membre.DoesNotExist:
            # Le membre n'existe pas encore, pas de notification
            pass
    
    @staticmethod
    def notifier_nouveau_membre(association, nouveau_membre, createur):
        """
        Notifie les membres d'une nouvelle adhésion
        """
        for adhesion in association.adhesions.all():
            if adhesion.membre != nouveau_membre:
                Notification.objects.create(
                    membre=adhesion.membre,
                    type_notification=TypeNotification.NOUVEAU_MEMBRE,
                    titre="Nouveau membre",
                    message=f"{nouveau_membre.get_full_name()} a rejoint l'association {association.name}"
                )