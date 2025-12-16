# Views pour la gestion des paiements
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import uuid

from ..models import (
    Association, Cotisation, Paiement, Adhesion,
    MethodePaiementModel, PaiementStatutModel, MethodePaiement, PaiementStatut
)


@login_required
def effectuer_paiement_view(request, cotisation_id):
    """Effectuer un paiement pour une cotisation"""
    cotisation = get_object_or_404(Cotisation, id=cotisation_id)
    association = cotisation.association
    
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
    
    # Vérifier si l'utilisateur a déjà payé cette cotisation
    paiement_existant = Paiement.objects.filter(
        cotisation=cotisation,
        membre=request.user,
        statut__statut=PaiementStatut.VALIDE
    ).first()
    
    if paiement_existant:
        messages.info(request, "Vous avez déjà payé cette cotisation")
        return redirect('mboa_assoc_app:liste_cotisations', association_id=association.id)
    
    if request.method == 'POST':
        methode = request.POST.get('methode')
        
        # Créer ou récupérer la méthode de paiement
        methode_obj, _ = MethodePaiementModel.objects.get_or_create(
            libelle=methode
        )
        
        # Créer ou récupérer le statut "en attente"
        statut_obj, _ = PaiementStatutModel.objects.get_or_create(
            statut=PaiementStatut.EN_ATTENTE
        )
        
        # Générer une référence unique
        reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        
        # Créer le paiement
        paiement = Paiement.objects.create(
            cotisation=cotisation,
            membre=request.user,
            montant=cotisation.montant,
            reference=reference,
            statut=statut_obj,
            methode=methode_obj
        )
        
        # Si c'est Mobile Money, simuler le processus
        if methode in [MethodePaiement.MOMO, MethodePaiement.OM]:
            # Simulation: valider automatiquement après 2 secondes
            statut_valide, _ = PaiementStatutModel.objects.get_or_create(
                statut=PaiementStatut.VALIDE
            )
            paiement.statut = statut_valide
            paiement.save()
            
            # Marquer la cotisation comme payée
            cotisation.date_paiement = timezone.now()
            cotisation.save()
            
            messages.success(
                request,
                f"Paiement de {cotisation.montant} FCFA effectué avec succès via {methode_obj.get_libelle_display()}"
            )
        else:
            messages.success(
                request,
                f"Paiement en attente de validation (Référence: {reference})"
            )
        
        return redirect('mboa_assoc_app:historique_paiements', association_id=association.id)
    
    context = {
        'cotisation': cotisation,
        'association': association,
        'methodes': MethodePaiement.choices
    }
    return render(request, 'paiements/effectuer.html', context)


@login_required
def historique_paiements_view(request, association_id):
    """Afficher l'historique des paiements d'une association"""
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
    
    # Récupérer les paiements
    if adhesion.role in ['PRESIDENT', 'TRESORIER']:
        # Président et trésorier voient tous les paiements
        paiements = Paiement.objects.filter(
            cotisation__association=association
        ).select_related('membre', 'cotisation', 'statut', 'methode').order_by('-date_paiement')
    else:
        # Les membres voient seulement leurs paiements
        paiements = Paiement.objects.filter(
            cotisation__association=association,
            membre=request.user
        ).select_related('cotisation', 'statut', 'methode').order_by('-date_paiement')
    
    # Calculer les statistiques
    total_collecte = sum(
        p.montant for p in paiements if p.statut.statut == PaiementStatut.VALIDE
    )
    
    context = {
        'association': association,
        'paiements': paiements,
        'total_collecte': total_collecte,
        'adhesion': adhesion
    }
    return render(request, 'paiements/historique.html', context)
