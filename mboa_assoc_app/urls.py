from django.urls import path
from . import views

app_name = 'mboa_assoc_app'  

urlpatterns = [
    # Créer une association
    path('association/creer/', views.create_association, name='create_association'),
    
    # Mes associations
    path('mes-associations/', views.my_associations, name='my_associations'),
    
    # Détails d'une association
    path('association/<int:id>/', views.association_detail, name='association_detail'),
    
    # Paramètres
    path('association/<int:id>/parametres/', views.association_settings, name='association_settings'),
    
    # Gestion des membres
    path('association/<int:id>/membres/', views.manage_members, name='manage_members'),
    path('association/<int:id>/membres/ajouter/', views.add_member, name='add_member'),
    path('association/<int:id>/membres/<int:member_id>/retirer/', views.remove_member, name='remove_member'),
    
    # Nominations
    path('association/<int:id>/nommer-president/', views.nominate_president, name='nominate_president'),
    path('association/<int:id>/nommer-tresorier/', views.nominate_treasurer, name='nominate_treasurer'),
    
    # Actions sur l'association
    path('association/<int:id>/archiver/', views.archive_association, name='archive_association'),
    path('association/<int:id>/supprimer/', views.delete_association, name='delete_association'),
]
