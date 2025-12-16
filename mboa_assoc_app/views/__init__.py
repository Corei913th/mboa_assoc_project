"""
Views package for mboa_assoc_app.
"""

from .landing_view import landing_view
from .register_view import register_view
from .verify_otp_view import verify_otp_view
from .login_view import login_view
from .logout_view import logout_view
from .profile_view import profile_view
from .dashboard_view import dashboard_view
from .association_views import (
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

__all__ = [
    'landing_view', 
    'register_view', 
    'verify_otp_view', 
    'login_view', 
    'logout_view', 
    'profile_view', 
    'dashboard_view',
    'create_association',
    'association_detail',
    'association_settings',
    'manage_members',
    'add_member',
    'remove_member',
    'nominate_president',
    'nominate_treasurer',
    'archive_association',
    'delete_association',
    'my_associations'
]
