from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from ..models import Adhesion, Role


class MemberService:
    """
    Service gérant la logique métier des membres d'associations
    """
    
    @staticmethod
    @transaction.atomic
    def add_member(association, user_to_add, role, added_by):
        """
        Ajoute un membre à une association
        
        Args:
            association: L'association
            user_to_add: L'utilisateur à ajouter (Membre)
            role: Le rôle à attribuer ('MEMBRE' par défaut)
            added_by: L'utilisateur qui ajoute le membre
            
        Returns:
            L'adhésion créée
            
        Raises:
            PermissionDenied: Si added_by n'a pas les permissions
            ValidationError: Si le membre existe déjà
        """
        # Vérifier les permissions
        if not MemberService._can_add_member(association, added_by):
            raise PermissionDenied("Vous n'avez pas la permission d'ajouter des membres")
        
        # Vérifier que l'utilisateur n'est pas déjà membre
        if Adhesion.objects.filter(association=association, membre=user_to_add).exists():
            raise ValidationError("Cet utilisateur est déjà membre de l'association")
        
        # Valider le rôle (ne peut pas ajouter un président ou trésorier directement)
        if role in [Role.PRESIDENT, Role.TRESORIER]:
            raise ValidationError("Utilisez la fonction de nomination pour ces rôles")
        
        # Créer l'adhésion
        adhesion = Adhesion.objects.create(
            association=association,
            membre=user_to_add,
            role=role if role else Role.MEMBRE
        )
        
        return adhesion
    
    @staticmethod
    @transaction.atomic
    def remove_member(association, adhesion, removed_by):
        """
        Retire un membre d'une association
        
        Args:
            association: L'association
            adhesion: L'adhésion à désactiver
            removed_by: L'utilisateur qui retire le membre
            
        Raises:
            PermissionDenied: Si removed_by n'a pas les permissions
            ValidationError: Si on tente de retirer le président
        """
        # Vérifier les permissions
        if not MemberService._can_remove_member(association, removed_by):
            raise PermissionDenied("Vous n'avez pas la permission de retirer des membres")
        
        # Empêcher de retirer le président
        if adhesion.role == Role.PRESIDENT:
            raise ValidationError("Impossible de retirer le président. Nommez d'abord un nouveau président.")
        
        # Désactiver l'adhésion (soft delete)
        adhesion.is_active = False
        adhesion.save()
    
    @staticmethod
    @transaction.atomic
    def nominate_president(association, new_president_user, nominated_by):
        """
        Nomme un nouveau président
        Le président actuel devient simple membre
        
        Args:
            association: L'association
            new_president_user: Le nouvel utilisateur à nommer président (Membre)
            nominated_by: L'utilisateur qui nomme (doit être le président actuel)
            
        Returns:
            La nouvelle adhésion président
            
        Raises:
            PermissionDenied: Si nominated_by n'est pas le président actuel
            ValidationError: Si le nouvel utilisateur n'est pas membre
        """
        # Vérifier que celui qui nomme est le président actuel
        current_president = Adhesion.objects.filter(
            association=association,
            role=Role.PRESIDENT,
            is_active=True
        ).first()
        
        if not current_president or current_president.membre != nominated_by:
            raise PermissionDenied("Seul le président actuel peut nommer un nouveau président")
        
        # Vérifier que le nouvel utilisateur est membre
        try:
            new_president_adhesion = Adhesion.objects.get(
                association=association,
                membre=new_president_user,
                is_active=True
            )
        except Adhesion.DoesNotExist:
            raise ValidationError("L'utilisateur doit d'abord être membre de l'association")
        
        # Rétrograder l'ancien président en simple membre
        current_president.role = Role.MEMBRE
        current_president.save()
        
        # Promouvoir le nouveau président
        new_president_adhesion.role = Role.PRESIDENT
        new_president_adhesion.save()
        
        return new_president_adhesion
    
    @staticmethod
    @transaction.atomic
    def nominate_treasurer(association, treasurer_user, nominated_by):
        """
        Nomme un trésorier
        S'il y avait déjà un trésorier, il devient simple membre
        
        Args:
            association: L'association
            treasurer_user: L'utilisateur à nommer trésorier (Membre)
            nominated_by: L'utilisateur qui nomme (doit être président)
            
        Returns:
            L'adhésion trésorier
            
        Raises:
            PermissionDenied: Si nominated_by n'est pas président
            ValidationError: Si l'utilisateur n'est pas membre
        """
        # Vérifier que celui qui nomme est président
        if not MemberService._is_president(association, nominated_by):
            raise PermissionDenied("Seul le président peut nommer le trésorier")
        
        # Vérifier que l'utilisateur est membre
        try:
            treasurer_adhesion = Adhesion.objects.get(
                association=association,
                membre=treasurer_user,
                is_active=True
            )
        except Adhesion.DoesNotExist:
            raise ValidationError("L'utilisateur doit d'abord être membre de l'association")
        
        # Rétrograder l'ancien trésorier s'il existe
        old_treasurer = Adhesion.objects.filter(
            association=association,
            role=Role.TRESORIER,
            is_active=True
        ).exclude(membre=treasurer_user).first()
        
        if old_treasurer:
            old_treasurer.role = Role.MEMBRE
            old_treasurer.save()
        
        # Promouvoir le nouveau trésorier
        treasurer_adhesion.role = Role.TRESORIER
        treasurer_adhesion.save()
        
        return treasurer_adhesion
    
    @staticmethod
    def _can_add_member(association, user):
        """Vérifie si un utilisateur peut ajouter des membres"""
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role__in=[Role.PRESIDENT, Role.TRESORIER],
            is_active=True
        ).exists()
    
    @staticmethod
    def _can_remove_member(association, user):
        """Vérifie si un utilisateur peut retirer des membres"""
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role__in=[Role.PRESIDENT, Role.TRESORIER],
            is_active=True
        ).exists()
    
    @staticmethod
    def _is_president(association, user):
        """Vérifie si un utilisateur est président"""
        return Adhesion.objects.filter(
            association=association,
            membre=user,
            role=Role.PRESIDENT,
            is_active=True
        ).exists()
    
    @staticmethod
    def get_member_role(association, user):
        """
        Récupère le rôle d'un utilisateur dans une association
        
        Returns:
            Le rôle ou None si pas membre
        """
        try:
            adhesion = Adhesion.objects.get(
                association=association,
                membre=user,
                is_active=True
            )
            return adhesion.role
        except Adhesion.DoesNotExist:
            return None