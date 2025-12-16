# Views pour la gestion des cotisations
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta

from ..models import Association, Cotisation, Adhesion, Role
from ..services.association_service import AssociationService


@login_required
def liste_cotisations_view(request, association_id):
    """Liste toutes les cotisations d'une association"""
    association = get_object_or_404(Association, id=association_id, is_active=True)
    
    # Vérifier que l'utilisateur est membre
    try:
        adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Récupérer toutes les cotisations
    cotisations = Cotisation.objects.filter(
        association=association
    ).order_by('-date_echeance')
    
    # Vérifier si l'utilisateur peut créer des cotisations (président ou trésorier)
    can_create = adhesion.role in [Role.PRESIDENT, Role.TRESORIER]
    
    context = {
        'association': association,
        'cotisations': cotisations,
        'can_create': can_create,
        'adhesion': adhesion
    }
    return render(request, 'cotisations/liste.html', context)


@login_required
def creer_cotisation_view(request, association_id):
    """Créer une nouvelle cotisation"""
    association = get_object_or_404(Association, id=association_id, is_active=True)
    
    # Vérifier que l'utilisateur est président ou trésorier
    try:
        adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
        if adhesion.role not in [Role.PRESIDENT, Role.TRESORIER]:
            raise PermissionDenied("Seuls le président et le trésorier peuvent créer des cotisations")
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    if request.method == 'POST':
        montant = request.POST.get('montant')
        type_cotisation = request.POST.get('type_cotisation')
        date_echeance = request.POST.get('date_echeance')
        
        try:
            cotisation = Cotisation.objects.create(
                association=association,
                montant=montant,
                type_cotisation=type_cotisation,
                date_echeance=date_echeance
            )
            messages.success(request, f"Cotisation '{type_cotisation}' créée avec succès")
            return redirect('mboa_assoc_app:liste_cotisations', association_id=association.id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
    
    # Proposer une date d'échéance par défaut (30 jours)
    date_defaut = (timezone.now() + timedelta(days=30)).date()
    
    context = {
        'association': association,
        'date_defaut': date_defaut
    }
    return render(request, 'cotisations/creer.html', context)
