# views/membres_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from ..models import Association, Adhesion, Membre, Invitation, Role
from ..services.invitation_service import InvitationService
from ..services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# VUES POUR LA GESTION DES MEMBRES
# ============================================================================

@login_required
def liste_membres_view(request, association_id):
    """
    Affiche la liste des membres d'une association.
    """
    association = get_object_or_404(Association, id=association_id)
    
    # Vérifier si l'utilisateur est membre de cette association
    try:
        adhesion_utilisateur = Adhesion.objects.get(
            membre=request.user,
            association=association
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Récupérer tous les membres avec leurs adhésions
    membres = Membre.objects.filter(
        adhesions__association=association
    ).select_related().prefetch_related('adhesions')
    
    # Récupérer les adhésions pour afficher les rôles
    adhésions_dict = {
        adhesion.membre_id: adhesion 
        for adhesion in Adhesion.objects.filter(association=association)
    }
    
    context = {
        'association': association,
        'membres': membres,
        'adhésions_dict': adhésions_dict,
        'user_adhesion': adhesion_utilisateur,
        'is_president': adhesion_utilisateur.role == Role.PRESIDENT,
    }
    
    return render(request, 'membres/liste.html', context)


@login_required
def inviter_membres_view(request, association_id):
    """
    Interface pour inviter des membres par téléphone.
    """
    association = get_object_or_404(Association, id=association_id)
    
    # Vérifier si l'utilisateur est président
    try:
        adhesion = Adhesion.objects.get(
            membre=request.user,
            association=association
        )
        if adhesion.role != Role.PRESIDENT:
            messages.error(request, "Seuls les présidents peuvent inviter des membres")
            return redirect('liste_membres', association_id=association_id)
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    if request.method == 'POST':
        telephone = request.POST.get('telephone', '').strip()
        
        if not telephone:
            messages.error(request, "Veuillez entrer un numéro de téléphone")
            return redirect('inviter_membres', association_id=association_id)
        
        # Créer l'invitation
        invitation, error = InvitationService.creer_invitation(
            association=association,
            telephone_invite=telephone,
            createur=request.user
        )
        
        if error:
            messages.error(request, error)
        else:
            # Envoyer une notification
            NotificationService.notifier_invitation(invitation)
            
            messages.success(
                request, 
                f"Invitation envoyée à {telephone}. Code: {invitation.code}"
            )
            logger.info(f"Invitation créée: {invitation.code} pour {telephone}")
        
        return redirect('inviter_membres', association_id=association_id)
    
    # Afficher les invitations en attente
    invitations_en_attente = Invitation.objects.filter(
        association=association,
        statut=Invitation.StatutInvitation.EN_ATTENTE
    )
    
    context = {
        'association': association,
        'invitations_en_attente': invitations_en_attente,
    }
    
    return render(request, 'membres/inviter.html', context)


@login_required
def accepter_invitation_view(request, code):
    """
    Page pour accepter ou refuser une invitation.
    """
    invitation = get_object_or_404(Invitation, code=code)
    
    # Vérifier que l'invitation est destinée à cet utilisateur
    if request.user.telephone != invitation.telephone_invite:
        messages.error(request, "Cette invitation ne vous est pas destinée")
        return redirect('mboa_assoc_app:dashboard')
    
    # Vérifier si l'invitation est toujours valide
    if not invitation.est_valide():
        messages.error(request, "Cette invitation a expiré ou a déjà été traitée")
        return redirect('mboa_assoc_app:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accepter':
            success, message = InvitationService.accepter_invitation(code, request.user)
            if success:
                messages.success(request, message)
                # Notifier les autres membres
                NotificationService.notifier_nouveau_membre(
                    invitation.association,
                    request.user,
                    invitation.createur
                )
                return redirect('liste_membres', association_id=invitation.association.id)
            else:
                messages.error(request, message)
        elif action == 'refuser':
            success, message = InvitationService.refuser_invitation(code, request.user)
            if success:
                messages.success(request, message)
                return redirect('mboa_assoc_app:dashboard')
            else:
                messages.error(request, message)
    
    context = {
        'invitation': invitation,
    }
    
    return render(request, 'membres/accepter_invitation.html', context)


@login_required
def changer_role_view(request, association_id, membre_id):
    """
    Modifie le rôle d'un membre (Président/Trésorier/Membre).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
    
    association = get_object_or_404(Association, id=association_id)
    
    # Vérifier si l'utilisateur est président
    try:
        adhesion_president = Adhesion.objects.get(
            membre=request.user,
            association=association,
            role=Role.PRESIDENT
        )
    except Adhesion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    # Récupérer le membre et son adhésion
    membre = get_object_or_404(Membre, id=membre_id)
    try:
        adhesion = Adhesion.objects.get(
            membre=membre,
            association=association
        )
    except Adhesion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Membre non trouvé'})
    
    # Vérifier qu'on ne change pas son propre rôle
    if membre == request.user:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas modifier votre propre rôle'})
    
    # Récupérer le nouveau rôle
    nouveau_role = request.POST.get('role')
    if nouveau_role not in dict(Role.choices).keys():
        return JsonResponse({'success': False, 'error': 'Rôle invalide'})
    
    # Si on nomme un nouveau président, l'ancien président devient simple membre
    if nouveau_role == Role.PRESIDENT:
        with transaction.atomic():
            # Ancien président devient membre
            adhesion_president.role = Role.MEMBRE
            adhesion_president.save()
            
            # Nouveau président
            adhesion.role = Role.PRESIDENT
            adhesion.save()
    else:
        adhesion.role = nouveau_role
        adhesion.save()
    
    logger.info(f"Rôle changé: {membre.username} -> {nouveau_role} dans {association.nom}")
    
    return JsonResponse({
        'success': True,
        'message': f'Rôle de {membre.get_full_name()} changé en {adhesion.get_role_display()}',
        'role_display': adhesion.get_role_display()
    })


@login_required
def exclure_membre_view(request, association_id, membre_id):
    """
    Exclut un membre d'une association.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
    
    association = get_object_or_404(Association, id=association_id)
    
    # Vérifier si l'utilisateur est président
    try:
        Adhesion.objects.get(
            membre=request.user,
            association=association,
            role=Role.PRESIDENT
        )
    except Adhesion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    # Récupérer le membre et son adhésion
    membre = get_object_or_404(Membre, id=membre_id)
    try:
        adhesion = Adhesion.objects.get(
            membre=membre,
            association=association
        )
    except Adhesion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Membre non trouvé'})
    
    # Vérifier qu'on ne s'exclut pas soi-même
    if membre == request.user:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous exclure vous-même'})
    
    # Supprimer l'adhésion
    nom_membre = membre.get_full_name()
    adhesion.delete()
    
    logger.info(f"Membre exclu: {membre.username} de {association.nom}")

    messages.success(request, f'{nom_membre} a été exclu de l\'association')
    
    return redirect('liste_membres', association_id=association_id)


@login_required
def detail_membre_view(request, association_id, membre_id):
    """
    Affiche le profil détaillé d'un membre.
    """
    association = get_object_or_404(Association, id=association_id)
    membre = get_object_or_404(Membre, id=membre_id)
    
    # Vérifier si l'utilisateur est membre de cette association
    try:
        Adhesion.objects.get(
            membre=request.user,
            association=association
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Récupérer l'adhésion du membre
    try:
        adhesion = Adhesion.objects.get(
            membre=membre,
            association=association
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Ce membre n'appartient pas à cette association")
        return redirect('liste_membres', association_id=association_id)
    
    context = {
        'association': association,
        'membre': membre,
        'adhesion': adhesion,
    }
    
    return render(request, 'membres/detail.html', context)


@login_required
def invitations_en_attente_view(request):
    """
    Affiche les invitations en attente de l'utilisateur.
    """
    invitations = Invitation.objects.filter(
        telephone_invite=request.user.telephone,
        statut=Invitation.StatutInvitation.EN_ATTENTE
    ).select_related('association', 'createur')
    
    # Filtrer les invitations valides
    invitations_valides = [inv for inv in invitations if inv.est_valide()]
    
    context = {
        'invitations': invitations_valides,
    }
    
    return render(request, 'membres/invitations_en_attente.html', context)