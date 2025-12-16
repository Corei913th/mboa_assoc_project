# URLs pour la gestion des associations

from django.urls import path, include
from .views import (
    landing_view,
    register_view,
    verify_otp_view,
    login_view,
    logout_view,
    profile_view,
    dashboard_view
)

from .views.membres_views import (
    liste_membres_view,
    inviter_membres_view,
    accepter_invitation_view,
    changer_role_view,
    exclure_membre_view,
    detail_membre_view,
    invitations_en_attente_view,
)

from . import views

app_name = 'mboa_assoc_app'

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),

    # Landing page (page d'accueil publique)
    path('', landing_view, name='landing'),

    # Dashboard (page d'accueil pour utilisateurs connectés)
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('auth/register/', register_view, name='register'),
    path('auth/verify-otp/', verify_otp_view, name='verify_otp'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', profile_view, name='profile'),

    # Associations URLs
    path('association/creer/', views.create_association, name='create_association'),
    path('mes-associations/', views.my_associations, name='my_associations'),
    path('association/<int:id>/', views.association_detail, name='association_detail'),
    path('association/<int:id>/parametres/', views.association_settings, name='association_settings'),
    
    # Gestion des membres (nouvelle structure)
    path('association/<int:id>/membres/', views.manage_members, name='manage_members'),
    path('association/<int:id>/membres/ajouter/', views.add_member, name='add_member'),
    path('association/<int:id>/membres/<int:member_id>/retirer/', views.remove_member, name='remove_member'),
    
    # Membres URLs (ancienne structure - à migrer)
    path('associations/<int:association_id>/membres/', liste_membres_view, name='liste_membres'),
    path('associations/<int:association_id>/inviter/', inviter_membres_view, name='inviter_membres'),
    path('invitations/accepter/<str:code>/', accepter_invitation_view, name='accepter_invitation'),
    path('associations/<int:association_id>/membres/<int:membre_id>/changer-role/', changer_role_view, name='changer_role'),
    path('associations/<int:association_id>/membres/<int:membre_id>/exclure/', exclure_membre_view, name='exclure_membre'),
    path('associations/<int:association_id>/membres/<int:membre_id>/detail/', detail_membre_view, name='detail_membre'),
    path('mes-invitations/', invitations_en_attente_view, name='mes_invitations'),
    
    # Nominations
    path('association/<int:id>/nommer-president/', views.nominate_president, name='nominate_president'),
    path('association/<int:id>/nommer-tresorier/', views.nominate_treasurer, name='nominate_treasurer'),
    
    # Actions sur l'association
    path('association/<int:id>/archiver/', views.archive_association, name='archive_association'),
    path('association/<int:id>/supprimer/', views.delete_association, name='delete_association'),
]
