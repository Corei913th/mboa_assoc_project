"""
Context processors pour ajouter des données globales
"""
from .models import Adhesion, Invitation

def user_associations(request):
    """Ajoute les associations de l'utilisateur au contexte global"""
    if request.user.is_authenticated:
        adhesions = Adhesion.objects.filter(
            membre=request.user,
            is_active=True
        ).select_related('association')
        
        # Compter les invitations en attente
        invitations_count = Invitation.objects.filter(
            telephone_invite=request.user.telephone,
            statut=Invitation.StatutInvitation.EN_ATTENTE
        ).count()
        
        return {
            'user_adhesions': adhesions,
            'user_associations_count': adhesions.count(),
            'invitations_en_attente_count': invitations_count
        }
    return {
        'invitations_en_attente_count': 0
    }
