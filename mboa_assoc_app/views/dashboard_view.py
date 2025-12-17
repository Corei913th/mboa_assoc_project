"""
Vue du tableau de bord principal.
Affiche un résumé des informations de l'utilisateur connecté.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Adhesion, Invitation


@login_required
def dashboard_view(request):
    from ..forms import AssociationForm
    from ..models import Cotisation, PaiementStatut, Paiement
    from django.utils import timezone
    from django.db.models import Q
    
    associations = Adhesion.objects.filter(membre=request.user, is_active=True).select_related('association').order_by('-date')
    
    # Récupérer et grouper les cotisations en attente par association
    cotisations_par_association = []
    cotisations_en_attente = []
    total_a_payer = 0
    
    for adhesion in associations:
        cotisations = Cotisation.objects.filter(
            association=adhesion.association,
            date_echeance__lte=timezone.now().date()
        ).exclude(
            paiements__membre=request.user,
            paiements__statut__statut=PaiementStatut.VALIDE
        )
        
        if cotisations.exists():
            assoc_total = sum(c.montant for c in cotisations)
            cotisations_par_association.append({
                'association': adhesion.association,
                'cotisations': list(cotisations),
                'total': assoc_total
            })
            cotisations_en_attente.extend(cotisations)
            total_a_payer += assoc_total
    
    phone_badge = {
        'type': 'success' if request.user.telephone_verifie else 'warning',
        'icon': 'check' if request.user.telephone_verifie else 'triangle-exclamation',
        'text': 'Vérifié' if request.user.telephone_verifie else 'Non vérifié'
    }
    
    location_badge = None if request.user.quartier else {'type': 'warning', 'icon': 'triangle-exclamation', 'text': 'Incomplet'}
    inscription_date = f"{request.user.date_inscription.strftime('%d/%m/%Y')}"
    
    user_name = request.user.get_full_name() or request.user.username
    
    return render(request, 'dashboard_new.html', {
        'associations': associations,
        'cotisations_par_association': cotisations_par_association,
        'cotisations_en_attente': cotisations_en_attente,
        'total_a_payer': total_a_payer,
        'today': timezone.now().date(),
        'form': AssociationForm(),
        'phone_badge': phone_badge,
        'location_badge': location_badge,
        'inscription_date': inscription_date,
        'page_title': f'Bienvenue, {user_name} !',
        'page_subtitle': 'Votre tableau de bord'
    })
