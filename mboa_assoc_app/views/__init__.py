"""
Views package for mboa_assoc_app.
"""

from .register_view import register_view
from .verify_otp_view import verify_otp_view
from .login_view import login_view
from .logout_view import logout_view
from .profile_view import profile_view
from .dashboard_view import dashboard_view

__all__ = ['register_view', 'verify_otp_view', 'login_view', 'logout_view', 'profile_view', 'dashboard_view']
