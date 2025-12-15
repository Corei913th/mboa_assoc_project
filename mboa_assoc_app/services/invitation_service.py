# services/invitation_service.py
import uuid
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from ..models import Invitation, Membre, Adhesion, Association, Role

class InvitationService:
    
    @staticmethod
    def generer_code_invitation():
        """Génère un code d'invitation unique"""
        return str(uuid.uuid4())[:8].upper()
    
    @staticmethod
    def creer_invitation(association, telephone_invite, createur):
        """
        Crée une nouvelle invitation
        """
        # Vérifier si l'utilisateur existe déjà
        try:
            membre_invite = Membre.objects.get(telephone=telephone_invite)
            # Vérifier s'il n'est pas déjà membre
            if Adhesion.objects.filter(membre=membre_invite, association=association).exists():
                return None, "Cet utilisateur est déjà membre de cette association"
        except Membre.DoesNotExist:
            pass  # L'utilisateur n'existe pas encore, c'est OK
        
        # Vérifier si une invitation est déjà en attente
        invitation_existante = Invitation.objects.filter(
            association=association,
            telephone_invite=telephone_invite,
            statut=Invitation.StatutInvitation.EN_ATTENTE
        ).first()
        
        if invitation_existante and invitation_existante.est_valide():
            return invitation_existante, "Une invitation est déjà en attente"
        
        # Créer la nouvelle invitation
        with transaction.atomic():
            invitation = Invitation.objects.create(
                code=InvitationService.generer_code_invitation(),
                association=association,
                telephone_invite=telephone_invite,
                createur=createur,
                date_expiration=timezone.now() + timedelta(days=7)
            )
        
        return invitation, None
    
    @staticmethod
    def accepter_invitation(code, membre):
        """
        Accepte une invitation
        """
        try:
            invitation = Invitation.objects.get(code=code)
            
            if not invitation.est_valide():
                return False, "L'invitation a expiré ou a déjà été traitée"
            
            if membre.telephone != invitation.telephone_invite:
                return False, "Cette invitation ne vous est pas destinée"
            
            with transaction.atomic():
                # Créer l'adhésion
                adhesion = Adhesion.objects.create(
                    membre=membre,
                    association=invitation.association,
                    date=timezone.now().date(),
                    role=Role.MEMBRE
                )
                
                # Mettre à jour l'invitation
                invitation.statut = Invitation.StatutInvitation.ACCEPTEE
                invitation.date_reponse = timezone.now()
                invitation.save()
            
            return True, "Invitation acceptée avec succès"
            
        except Invitation.DoesNotExist:
            return False, "Code d'invitation invalide"
    
    @staticmethod
    def refuser_invitation(code, membre):
        """
        Refuse une invitation
        """
        try:
            invitation = Invitation.objects.get(code=code)
            
            if not invitation.est_valide():
                return False, "L'invitation a expiré ou a déjà été traitée"
            
            if membre.telephone != invitation.telephone_invite:
                return False, "Cette invitation ne vous est pas destinée"
            
            invitation.statut = Invitation.StatutInvitation.REFUSEE
            invitation.date_reponse = timezone.now()
            invitation.save()
            
            return True, "Invitation refusée"
            
        except Invitation.DoesNotExist:
            return False, "Code d'invitation invalide"