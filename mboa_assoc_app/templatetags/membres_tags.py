# mboa_assoc_app/templatetags/membres_tags.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Récupère une valeur d'un dictionnaire par clé"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def jours_restants(date_expiration):
    """Calcule les jours restants avant expiration"""
    from django.utils import timezone
    if not date_expiration:
        return 0
    delta = date_expiration - timezone.now()
    return max(0, delta.days)

@register.filter
def get_key(dictionary, key):
    """Alias pour get_item"""
    return dictionary.get(key) if dictionary else None

@register.filter
def in_role(adhesion, role_name):
    """Vérifie si l'adhésion a un certain rôle"""
    return adhesion.role == role_name