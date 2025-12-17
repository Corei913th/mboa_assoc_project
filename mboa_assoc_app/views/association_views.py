# Views pour la gestion des associations
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from ..models import Association, Adhesion, Membre, Role
from ..forms import (
    AssociationForm, 
    AddMemberForm, 
    NominatePresidentForm,
    NominateTreasurerForm,
    SearchMemberForm
)
from ..services.association_service import AssociationService
from ..services.member_service import MemberService


@login_required
def create_association(request):
    """
    Vue pour créer une nouvelle association
    L'utilisateur devient automatiquement président
    """
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Utiliser le service pour créer l'association
                association = AssociationService.create_association(
                    form.cleaned_data,
                    request.user
                )
                messages.success(
                    request, 
                    f"L'association '{association.name}' a été créée avec succès !"
                )
                return redirect('mboa_assoc_app:my_associations')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {str(e)}")
    else:
        form = AssociationForm()
    
    context = {
        'form': form,
        'page_title': 'Créer une association'
    }
    return render(request, 'associations/create_association.html', context)


@login_required
def association_detail(request, id):
    """
    Vue pour afficher les détails d'une association
    """
    association = get_object_or_404(Association, id=id, is_active=True)
    
    # Vérifier que l'utilisateur est membre
    try:
        user_adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:my_associations')
    
    # Récupérer les membres
    members = association.get_all_members()
    president = association.get_president()
    treasurer = association.get_treasurer()
    
    context = {
        'association': association,
        'adhesion': user_adhesion,
        'members': members,
        'president': president,
        'treasurer': treasurer,
        'page_title': association.name
    }
    return render(request, 'associations/association_detail.html', context)


@login_required
def association_settings(request, id):
    """
    Vue pour gérer les paramètres d'une association
    Accessible uniquement au président
    """
    association = get_object_or_404(Association, id=id, is_active=True)
    
    # Récupérer l'adhésion de l'utilisateur
    try:
        adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Vérifier que l'utilisateur est président
    if adhesion.role != Role.PRESIDENT:
        messages.error(request, "Seul le président peut modifier les paramètres")
        return redirect('mboa_assoc_app:association_detail', id=association.id)
    
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES, instance=association)
        if form.is_valid():
            try:
                AssociationService.update_association(
                    association,
                    form.cleaned_data,
                    request.user
                )
                messages.success(request, "Les paramètres ont été mis à jour avec succès")
                return redirect('mboa_assoc_app:association_detail', id=association.id)
            except PermissionDenied as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Erreur : {str(e)}")
    else:
        form = AssociationForm(instance=association)
    
    context = {
        'form': form,
        'association': association,
        'page_title': f'Paramètres - {association.name}'
    }
    return render(request, 'associations/association_settings.html', context)


@login_required
def manage_members(request, id):
    """
    Vue pour gérer les membres d'une association
    Accessible au président et au trésorier
    """
    association = get_object_or_404(Association, id=id, is_active=True)
    
    # Récupérer l'adhésion de l'utilisateur
    try:
        adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Vérifier les permissions
    if adhesion.role not in [Role.PRESIDENT, Role.TRESORIER]:
        messages.error(request, "Vous n'avez pas la permission de gérer les membres")
        return redirect('mboa_assoc_app:association_detail', id=association.id)
    
    # Récupérer les membres
    members = association.get_all_members()
    president = association.get_president()
    
    # Formulaires
    add_member_form = AddMemberForm(association=association)
    nominate_president_form = NominatePresidentForm(association=association)
    nominate_treasurer_form = NominateTreasurerForm(association=association)
    search_form = SearchMemberForm()
    
    # Gestion de la recherche d'utilisateurs
    available_users = Membre.objects.none()
    if request.GET.get('search'):
        search_query = request.GET.get('search')
        existing_members = Adhesion.objects.filter(
            association=association
        ).values_list('membre_id', flat=True)
        
        available_users = Membre.objects.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        ).exclude(id__in=existing_members)[:10]
    
    context = {
        'association': association,
        'members': members,
        'president': president,
        'adhesion': adhesion,
        'add_member_form': add_member_form,
        'nominate_president_form': nominate_president_form,
        'nominate_treasurer_form': nominate_treasurer_form,
        'search_form': search_form,
        'available_users': available_users,
        'page_title': f'Gestion des membres - {association.name}'
    }
    return render(request, 'associations/manage_members.html', context)


@login_required
def add_member(request, id):
    """
    Ajoute un membre à l'association
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:manage_members', id=id)
    
    association = get_object_or_404(Association, id=id, is_active=True)
    
    user_id = request.POST.get('user_id')
    try:
        user_to_add = Membre.objects.get(id=user_id)
        MemberService.add_member(association, user_to_add, Role.MEMBRE, request.user)
        messages.success(request, f"{user_to_add.username} a été ajouté à l'association")
    except Membre.DoesNotExist:
        messages.error(request, "Utilisateur introuvable")
    except PermissionDenied as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('mboa_assoc_app:manage_members', id=id)


@login_required
def remove_member(request, id, member_id):
    """
    Retire un membre de l'association
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:manage_members', id=id)
    
    association = get_object_or_404(Association, id=id, is_active=True)
    adhesion = get_object_or_404(Adhesion, id=member_id, association=association)
    
    try:
        MemberService.remove_member(association, adhesion, request.user)
        messages.success(request, f"{adhesion.membre.username} a été retiré de l'association")
    except PermissionDenied as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('mboa_assoc_app:manage_members', id=id)


@login_required
def nominate_president(request, id):
    """
    Nomme un nouveau président
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:manage_members', id=id)
    
    association = get_object_or_404(Association, id=id, is_active=True)
    form = NominatePresidentForm(request.POST, association=association)
    
    if form.is_valid():
        try:
            new_president = form.cleaned_data['new_president']
            MemberService.nominate_president(association, new_president, request.user)
            messages.success(request, f"{new_president.username} est maintenant président")
        except PermissionDenied as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "Formulaire invalide")
    
    return redirect('mboa_assoc_app:manage_members', id=id)


@login_required
def nominate_treasurer(request, id):
    """
    Nomme un trésorier
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:manage_members', id=id)
    
    association = get_object_or_404(Association, id=id, is_active=True)
    form = NominateTreasurerForm(request.POST, association=association)
    
    if form.is_valid():
        try:
            treasurer = form.cleaned_data['treasurer']
            MemberService.nominate_treasurer(association, treasurer, request.user)
            messages.success(request, f"{treasurer.username} est maintenant trésorier")
        except PermissionDenied as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, str(e))
    else:
        messages.error(request, "Formulaire invalide")
    
    return redirect('mboa_assoc_app:manage_members', id=id)


@login_required
def archive_association(request, id):
    """
    Archive une association
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:association_detail', id=id)
    
    association = get_object_or_404(Association, id=id, is_active=True)
    
    try:
        AssociationService.archive_association(association, request.user)
        messages.success(request, f"L'association '{association.name}' a été archivée")
        return redirect('mboa_assoc_app:my_associations')
    except PermissionDenied as e:
        messages.error(request, str(e))
        return redirect('mboa_assoc_app:association_detail', id=id)
    except Exception as e:
        messages.error(request, f"Erreur : {str(e)}")
        return redirect('mboa_assoc_app:association_detail', id=id)


@login_required
def delete_association(request, id):
    """
    Supprime définitivement une association
    """
    if request.method != 'POST':
        return redirect('mboa_assoc_app:association_detail', id=id)
    
    association = get_object_or_404(Association, id=id)
    association_name = association.name
    
    try:
        AssociationService.delete_association(association, request.user)
        messages.success(request, f"L'association '{association_name}' a été supprimée définitivement")
        return redirect('mboa_assoc_app:my_associations')
    except PermissionDenied as e:
        messages.error(request, str(e))
        return redirect('mboa_assoc_app:association_detail', id=id)
    except Exception as e:
        messages.error(request, f"Erreur : {str(e)}")
        return redirect('mboa_assoc_app:association_detail', id=id)


@login_required
def my_associations(request):
    from ..forms import AssociationForm
    
    # Récupérer les adhésions (pas les associations directement)
    associations = Adhesion.objects.filter(
        membre=request.user,
        is_active=True,
        association__is_active=True
    ).select_related('association').order_by('-date')
    
    return render(request, 'associations/my_associations.html', {
        'associations': associations,
        'form': AssociationForm()
    })
