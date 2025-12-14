# URLs pour la gestion des associations


from django.urls import path
from .views import (
    register_view,
    verify_otp_view,
    login_view,
    logout_view,
    profile_view,
    dashboard_view
)

urlpatterns = [
    # Dashboard
    path('', dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('auth/register/', register_view, name='register'),
    path('auth/verify-otp/', verify_otp_view, name='verify_otp'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', profile_view, name='profile'),
]
