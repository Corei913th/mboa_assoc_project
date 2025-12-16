from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from ..models import Association, Adhesion, Role


class AssociationService:
    """
    Service gérant la logique métier des associations
    """
    
    @staticmethod
    @transaction.atomic
    def create_association(data, user):
        """
        Crée une nouvelle association et nomme le créateur comme président
        
        Args:
            data: Dictionnaire contenant les données de l'association
            user: L'utilisateur qui crée l'association (Membre)
            
        Returns:
            L'association créée
        """
        # Créer l'association
        association = Association.objects.create(
            name=data['name'],
            type=data['type'],
            description=data.get('description', ''),
            registration_number=data.get('registration_number', ''),
            legal_status=data.get('legal_status', ''),
            creation_date=data.get('creation_date'),
            logo=data.get('logo'),
            created_by=user
        )
        
        # Créer l'adhésion avec rôle président
        Adhesion.objects.create(
            association=association,
            membre=user,
            role=Role.PRESIDENT
        )
        
        return association
    
    @staticmethod
    @transaction.atomic
    def update_association(association, data, user):
        """
        Met à jour les informations d'une association
        
        Args:
            association: L'association à modifier
            data: Dictionnaire contenant les nouvelles données
            user: L'utilisateur qui effectue la modification
            
        Returns:
            L'association modifiée
            
        Raises:
            PermissionDenied: Si l'utilisateur n'est pas président
        """
        # Vérifier que l'utilisateur est président
        if not AssociationService.is_president(association, user):
            raise PermissionDenied("Seul le président peut modifier l'association")
        
        # Mettre à jour les champs
        association.name = data.get('name', association.name)
        association.type = data.get('type', association.type)
        association.description = data.get('description', association.description)
        association.registration_number = data.get('registration_number', association.registration_number)
        association.legal_status = data.get('legal_status', association.legal_status)
        association.creation_date = data.get('creation_date', association.creation_date)
        
        # Gérer le logo
        if 'logo' in data and data['logo']:
            association.logo = data['logo']
        
        association.save()
        return association
    
    @staticmethod
    @transaction.atomic
    def archive_association(association, user):
        """
        Archive une association (soft delete)
        
        Args:
            association: L'association à archiver
            user: L'utilisateur qui effectue l'action
            
        Raises:
            PermissionDenied: Si l'utilisateur n'est pas président
        """
        if not AssociationService.is_president(association, user):
            raise PermissionDenied("Seul le président peut archiver l'association")
        
        association.is_archived = True
        association.archived_at = timezone.now()
        association.save()
    
    @staticmethod
    @transaction.atomic
    def unarchive_association(association, user):
        """
        Désarchive une association
        
        Args:
            association: L'association à désarchiver
            user: L'utilisateur qui effectue l'action
            
        Raises:
            PermissionDenied: Si l'utilisateur n'est pas président
        """
        if not AssociationService.is_president(association, user):
            raise PermissionDenied("Seul le président peut désarchiver l'association")
        
        association.is_archived = False
        association.archived_at = None
        association.save()
    
    @staticmethod
    @transaction.atomic
    def delete_association(association, user):
        """
        Supprime définitivement une association
        
        Args:
            association: L'association à supprimer
            user: L'utilisateur qui effectue l'action
            
        Raises:
            PermissionDenied: Si l'utilisateur n'est pas président
        """
        if not AssociationService.is_president(association, user):
            raise PermissionDenied("Seul le président peut supprimer l'association")
        
        association.delete()
    
    @staticmethod
    def is_president(association, user):
        """
        Vérifie si un utilisateur est le président d'une association
        
        Args:
            association: L'association
            user: L'utilisateur à vérifier
            
        Returns:
            True si l'utilisateur est président, False sinon
        """
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role=Role.PRESIDENT,
            is_active=True
        ).exists()
    
    @staticmethod
    def is_treasurer(association, user):
        """
        Vérifie si un utilisateur est le trésorier d'une association
        
        Args:
            association: L'association
            user: L'utilisateur à vérifier
            
        Returns:
            True si l'utilisateur est trésorier, False sinon
        """
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role=Role.TRESORIER,
            is_active=True
        ).exists()
    
    @staticmethod
    def can_manage_settings(association, user):
        """
        Vérifie si un utilisateur peut gérer les paramètres (président uniquement)
        
        Args:
            association: L'association
            user: L'utilisateur à vérifier
            
        Returns:
            True si l'utilisateur peut gérer, False sinon
        """
        return AssociationService.is_president(association, user)
    
    @staticmethod
    def can_manage_members(association, user):
        """
        Vérifie si un utilisateur peut gérer les membres (président + trésorier)
        
        Args:
            association: L'association
            user: L'utilisateur à vérifier
            
        Returns:
            True si l'utilisateur peut gérer les membres, False sinon
        """
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role__in=[Role.PRESIDENT, Role.TRESORIER],
            is_active=True
        ).exists()
    
    @staticmethod
    def get_user_associations(user):
        """
        Récupère toutes les associations d'un utilisateur
        
        Args:
            user: L'utilisateur
            
        Returns:
            QuerySet des associations
        """
        return Association.objects.filter(
            adhesions__membre=user,
            adhesions__is_active=True,
            is_active=True
        ).distinct()