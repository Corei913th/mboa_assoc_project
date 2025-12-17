"""
Template tags pour les permissions
DRY: Une seule source de vérité pour toutes les permissions
"""
from django import template
from ..models import Role

register = template.Library()

@register.filter
def can_manage_members(adhesion):
    """Vérifie si le membre peut gérer d'autres membres"""
    return adhesion.role in [Role.PRESIDENT, Role.TRESORIER]

@register.filter
def can_create_cotisation(adhesion):
    """Vérifie si le membre peut créer des cotisations"""
    return adhesion.role in [Role.PRESIDENT, Role.TRESORIER]

@register.filter
def can_invite_members(adhesion):
    """Vérifie si le membre peut inviter"""
    return adhesion.role == Role.PRESIDENT

@register.filter
def can_change_roles(adhesion):
    """Vérifie si le membre peut changer les rôles"""
    return adhesion.role == Role.PRESIDENT

@register.filter
def can_exclude_members(adhesion):
    """Vérifie si le membre peut exclure"""
    return adhesion.role == Role.PRESIDENT

@register.filter
def can_view_all_payments(adhesion):
    """Vérifie si le membre peut voir tous les paiements"""
    return adhesion.role in [Role.PRESIDENT, Role.TRESORIER]

@register.filter
def can_export_data(adhesion):
    """Vérifie si le membre peut exporter les données"""
    return adhesion.role in [Role.PRESIDENT, Role.TRESORIER]

@register.filter
def is_president(adhesion):
    """Vérifie si le membre est président"""
    return adhesion.role == Role.PRESIDENT

@register.filter
def is_treasurer(adhesion):
    """Vérifie si le membre est trésorier"""
    return adhesion.role == Role.TRESORIER

@register.filter
def is_member(adhesion):
    """Vérifie si le membre est un simple membre"""
    return adhesion.role == Role.MEMBRE

@register.simple_tag
def get_role_icon(role):
    """Retourne l'icône correspondant au rôle"""
    icons = {
        Role.PRESIDENT: 'fa-crown',
        Role.TRESORIER: 'fa-coins',
        Role.MEMBRE: 'fa-user'
    }
    return icons.get(role, 'fa-user')

@register.simple_tag
def get_role_color(role):
    """Retourne la couleur correspondant au rôle"""
    colors = {
        Role.PRESIDENT: 'warning',
        Role.TRESORIER: 'accent',
        Role.MEMBRE: 'muted'
    }
    return colors.get(role, 'muted')
