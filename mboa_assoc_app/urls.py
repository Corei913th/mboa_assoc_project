from django.urls import path
from . import views

app_name = 'mboa_assoc_app'

urlpatterns = [
    path('paiements/', views.PaiementListView.as_view(), name='paiement_list'),
    path('paiements/<int:pk>/', views.PaiementDetailView.as_view(), name='paiement_detail'),
    path('paiements/creer/', views.PaiementCreateView.as_view(), name='paiement_create'),
    path('cotisations/', views.CotisationListView.as_view(), name='cotisation_list'),
    path('cotisations/creer/', views.CotisationCreateView.as_view(), name='cotisation_create'),
    path('cotisations/<int:pk>/', views.CotisationDetailView.as_view(), name='cotisation_detail'),
    
]
