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

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),

    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('auth/register/', register_view, name='register'),
    path('auth/verify-otp/', verify_otp_view, name='verify_otp'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', profile_view, name='profile'),


    # Membres URLs
    path('associations/<int:association_id>/membres/', liste_membres_view, name='liste_membres'),
    path('associations/<int:association_id>/inviter/', inviter_membres_view, name='inviter_membres'),
    path('invitations/accepter/<str:code>/', accepter_invitation_view, name='accepter_invitation'),
    path('associations/<int:association_id>/membres/<int:membre_id>/changer-role/', changer_role_view, name='changer_role'),
    path('associations/<int:association_id>/membres/<int:membre_id>/exclure/', exclure_membre_view, name='exclure_membre'),
    path('associations/<int:association_id>/membres/<int:membre_id>/detail/', detail_membre_view, name='detail_membre'),
    path('mes-invitations/', invitations_en_attente_view, name='mes_invitations'),
]
