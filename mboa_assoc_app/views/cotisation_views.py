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
    from ..forms import CotisationForm
    from datetime import timedelta
    
    association = get_object_or_404(Association, id=association_id, is_active=True)
    
    try:
        adhesion = Adhesion.objects.get(association=association, membre=request.user, is_active=True)
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    cotisations = Cotisation.objects.filter(association=association).order_by('-date_echeance')
    initial_data = {'date_echeance': (timezone.now() + timedelta(days=30)).date()}
    
    return render(request, 'cotisations/liste.html', {
        'association': association,
        'cotisations': cotisations,
        'adhesion': adhesion,
        'form': CotisationForm(initial=initial_data),
        'today': timezone.now().date()
    })


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
        from ..forms import CotisationForm
        form = CotisationForm(request.POST)
        
        if form.is_valid():
            try:
                cotisation = Cotisation.objects.create(
                    association=association,
                    montant=form.cleaned_data['montant'],
                    type_cotisation=form.cleaned_data['type_cotisation'],
                    date_echeance=form.cleaned_data['date_echeance']
                )
                messages.success(request, f"Cotisation '{cotisation.type_cotisation}' créée avec succès")
                
                next_url = request.GET.get('next', '')
                if next_url == 'dashboard':
                    return redirect('mboa_assoc_app:association_dashboard', association_id=association.id)
                return redirect('mboa_assoc_app:liste_cotisations', association_id=association.id)
            except Exception as e:
                messages.error(request, f"Erreur lors de la création: {str(e)}")
        else:
            messages.error(request, "Formulaire invalide. Vérifiez les informations saisies.")
    
    # Proposer une date d'échéance par défaut (30 jours)
    date_defaut = (timezone.now() + timedelta(days=30)).date()
    
    context = {
        'association': association,
        'date_defaut': date_defaut
    }
    return render(request, 'cotisations/creer.html', context)
