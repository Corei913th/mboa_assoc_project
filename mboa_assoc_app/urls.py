# URLs pour la gestion des associations

from django.urls import path, include
from .views import (
    landing_view,
    register_view, 
    verify_otp_view,  
    login_view,
    logout_view,
    profile_view,
    dashboard_view,
    create_association,
    association_detail,
    association_settings,
    manage_members,
    add_member,
    remove_member,
    nominate_president,
    nominate_treasurer,
    archive_association,
    delete_association,
    my_associations
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

app_name = 'mboa_assoc_app'

urlpatterns = [
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
    path('association/creer/', create_association, name='create_association'),
    path('mes-associations/', my_associations, name='my_associations'),
    path('association/<int:id>/', association_detail, name='association_detail'),
    path('association/<int:id>/parametres/', association_settings, name='association_settings'),
    
    # Gestion des membres (nouvelle structure)
    path('association/<int:id>/membres/', manage_members, name='manage_members'),
    path('association/<int:id>/membres/ajouter/', add_member, name='add_member'),
    path('association/<int:id>/membres/<int:member_id>/retirer/', remove_member, name='remove_member'),
    
    # Membres URLs (ancienne structure - à migrer)
    path('associations/<int:association_id>/membres/', liste_membres_view, name='liste_membres'),
    path('associations/<int:association_id>/inviter/', inviter_membres_view, name='inviter_membres'),
    path('invitations/accepter/<str:code>/', accepter_invitation_view, name='accepter_invitation'),
    path('associations/<int:association_id>/membres/<int:membre_id>/changer-role/', changer_role_view, name='changer_role'),
    path('associations/<int:association_id>/membres/<int:membre_id>/exclure/', exclure_membre_view, name='exclure_membre'),
    path('associations/<int:association_id>/membres/<int:membre_id>/detail/', detail_membre_view, name='detail_membre'),
    path('mes-invitations/', invitations_en_attente_view, name='mes_invitations'),
    
    # Nominations
    path('association/<int:id>/nommer-president/', nominate_president, name='nominate_president'),
    path('association/<int:id>/nommer-tresorier/', nominate_treasurer, name='nominate_treasurer'),
    
    # Actions sur l'association
    path('association/<int:id>/archiver/', archive_association, name='archive_association'),
    path('association/<int:id>/supprimer/', delete_association, name='delete_association'),
]
