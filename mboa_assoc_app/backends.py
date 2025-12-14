"""
Backend d'authentification personnalisé pour utiliser le téléphone au lieu du username.
Permet aux utilisateurs de se connecter avec leur numéro de téléphone.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Membre = get_user_model()


class PhoneBackend(ModelBackend):
    """
    Backend d'authentification qui utilise le numéro de téléphone au lieu du username.
    
    Ce backend permet aux utilisateurs de se connecter avec leur numéro de téléphone
    et leur mot de passe, conformément aux requirements 4.1 et 4.2.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur avec son numéro de téléphone et mot de passe.
        
        Args:
            request: La requête HTTP
            username: Le numéro de téléphone (nommé username pour compatibilité avec Django)
            password: Le mot de passe
            
        Returns:
            Membre: L'utilisateur authentifié ou None si l'authentification échoue
        """
        try:
            # Chercher l'utilisateur par téléphone au lieu de username
            user = Membre.objects.get(telephone=username)
            
            # Vérifier le mot de passe
            if user.check_password(password):
                return user
        except Membre.DoesNotExist:
            # Exécuter le hashage du mot de passe pour éviter les attaques par timing
            Membre().set_password(password)
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: L'ID de l'utilisateur
            
        Returns:
            Membre: L'utilisateur ou None s'il n'existe pas
        """
        try:
            return Membre.objects.get(pk=user_id)
        except Membre.DoesNotExist:
            return None
