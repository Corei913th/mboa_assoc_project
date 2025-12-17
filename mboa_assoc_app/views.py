from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Paiement, Cotisation

# Liste des paiements
class PaiementListView(ListView):
    model = Paiement
    template_name = 'paiements/paiement_list.html'
    context_object_name = 'paiements'

# Détail d'un paiement
class PaiementDetailView(DetailView):
    model = Paiement
    template_name = 'paiements/paiement_detail.html'
    context_object_name = 'paiement'

# Création d'un paiement
class PaiementCreateView(CreateView):
    model = Paiement
    template_name = 'paiements/paiement_create.html'
    fields = ['cotisation', 'membre', 'montant', 'reference', 'statut', 'methode']
    success_url = reverse_lazy('mboa_assoc_app:paiement_list')

class CotisationListView(ListView):
    model = Cotisation
    template_name = 'mboa_assoc_app/cotisation_list.html'
    context_object_name = 'cotisations'

class CotisationDetailView(DetailView):
    model = Cotisation
    template_name = 'mboa_assoc_app/cotisation_detail.html'
    context_object_name = 'cotisation'

class CotisationCreateView(CreateView):
    model = Cotisation
    template_name = 'mboa_assoc_app/cotisation_form.html'
    fields = ['nom', 'montant']
    success_url = reverse_lazy('mboa_assoc_app:cotisation_list')

