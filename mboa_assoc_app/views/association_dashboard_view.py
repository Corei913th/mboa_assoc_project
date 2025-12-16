# View pour le dashboard d'une association
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse

from ..models import (
    Association, Adhesion, Cotisation, Paiement,
    PaiementStatut, Role
)


@login_required
def association_dashboard_view(request, association_id):
    """Dashboard d'une association avec statistiques"""
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
    
    # Statistiques des membres
    total_membres = Adhesion.objects.filter(
        association=association,
        is_active=True
    ).count()
    
    president = association.get_president()
    tresorier = association.get_treasurer()
    
    # Statistiques des cotisations
    cotisations_actives = Cotisation.objects.filter(
        association=association,
        date_echeance__gte=timezone.now().date()
    ).count()
    
    # Statistiques des paiements ce mois
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    paiements_mois = Paiement.objects.filter(
        cotisation__association=association,
        date_paiement__gte=debut_mois,
        statut__statut=PaiementStatut.VALIDE
    )
    
    montant_collecte_mois = paiements_mois.aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    # Prochaine échéance
    prochaine_cotisation = Cotisation.objects.filter(
        association=association,
        date_echeance__gte=timezone.now().date()
    ).order_by('date_echeance').first()
    
    # Derniers paiements
    derniers_paiements = Paiement.objects.filter(
        cotisation__association=association
    ).select_related('membre', 'cotisation', 'statut').order_by('-date_paiement')[:5]
    
    # Membres récents
    membres_recents = Adhesion.objects.filter(
        association=association,
        is_active=True
    ).select_related('membre').order_by('-date')[:5]
    
    context = {
        'association': association,
        'adhesion': adhesion,
        'total_membres': total_membres,
        'president': president,
        'tresorier': tresorier,
        'cotisations_actives': cotisations_actives,
        'montant_collecte_mois': montant_collecte_mois,
        'prochaine_cotisation': prochaine_cotisation,
        'derniers_paiements': derniers_paiements,
        'membres_recents': membres_recents,
    }
    return render(request, 'associations/dashboard.html', context)


@login_required
def export_membres_csv_view(request, association_id):
    """Exporter la liste des membres en CSV"""
    association = get_object_or_404(Association, id=association_id, is_active=True)
    
    # Vérifier que l'utilisateur est président ou trésorier
    try:
        adhesion = Adhesion.objects.get(
            association=association,
            membre=request.user,
            is_active=True
        )
        if adhesion.role not in [Role.PRESIDENT, Role.TRESORIER]:
            messages.error(request, "Seuls le président et le trésorier peuvent exporter les membres")
            return redirect('mboa_assoc_app:association_dashboard', association_id=association.id)
    except Adhesion.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette association")
        return redirect('mboa_assoc_app:dashboard')
    
    # Créer la réponse CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="membres_{association.name}_{timezone.now().strftime("%Y%m%d")}.csv"'
    response.write('\ufeff')  # BOM pour Excel
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Téléphone', 'Email', 'Rôle', 'Date d\'adhésion', 'Statut'])
    
    # Récupérer tous les membres
    adhesions = Adhesion.objects.filter(
        association=association,
        is_active=True
    ).select_related('membre').order_by('role', 'date')
    
    for adhesion in adhesions:
        membre = adhesion.membre
        writer.writerow([
            membre.last_name,
            membre.first_name,
            membre.telephone,
            membre.email,
            adhesion.get_role_display(),
            adhesion.date.strftime('%d/%m/%Y'),
            'Actif' if adhesion.is_active else 'Inactif'
        ])
    
    return response
