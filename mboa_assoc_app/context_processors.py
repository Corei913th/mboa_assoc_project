# context_processors.py
def notifications_context(request):
    """
    Ajoute le nombre d'invitations en attente au contexte global.
    """
    if request.user.is_authenticated:
        from .models import Invitation
        invitations_count = Invitation.objects.filter(
            telephone_invite=request.user.telephone,
            statut=Invitation.StatutInvitation.EN_ATTENTE
        ).count()
        
        # Filtrer les invitations valides
        invitations = Invitation.objects.filter(
            telephone_invite=request.user.telephone,
            statut=Invitation.StatutInvitation.EN_ATTENTE
        )
        invitations_valides_count = sum(1 for inv in invitations if inv.est_valide())
        
        return {
            'invitations_en_attente_count': invitations_valides_count
        }
    return {}