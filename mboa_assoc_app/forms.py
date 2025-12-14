from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Membre
import re


class TailwindTextInput(forms.TextInput):
    """Widget TextInput avec classes shadcn réutilisables"""
    def __init__(self, attrs=None, placeholder=''):
        default_attrs = {
            'class': 'form-input',
            'placeholder': placeholder
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindPasswordInput(forms.PasswordInput):
    """Widget PasswordInput avec classes shadcn réutilisables"""
    def __init__(self, attrs=None, placeholder=''):
        default_attrs = {
            'class': 'form-input',
            'placeholder': placeholder
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindFileInput(forms.ClearableFileInput):
    """Widget FileInput avec classes shadcn réutilisables"""
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-input'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class TailwindSelect(forms.Select):
    """Widget Select avec classes shadcn réutilisables"""
    def __init__(self, attrs=None, choices=()):
        default_attrs = {
            'class': 'form-input'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)


# ============================================================================
# VALIDATEURS PERSONNALISÉS
# ============================================================================

def validate_cameroon_phone(value):
    """
    Valide le format du numéro de téléphone camerounais.
    Formats acceptés:
    - +237683793777 (avec +237)
    - 237683793777 (avec 237)
    - 683793777 (9 chiffres commençant par 6)
    """
    # Accepter: +237 ou 237 (optionnel) + 6 + 8 chiffres
    pattern = r'^(\+?237)?[6][0-9]{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Format invalide. Utilisez: +237683793777 ou 683793777',
            code='invalid_phone'
        )


def validate_otp_code(value):
    """
    Valide le format du code OTP.
    Doit contenir exactement 6 chiffres.
    """
    if not re.match(r'^[0-9]{6}$', value):
        raise ValidationError(
            'Le code OTP doit contenir exactement 6 chiffres',
            code='invalid_otp'
        )


def validate_photo_size(value):
    """
    Valide la taille du fichier photo.
    Taille maximale: 5MB
    """
    max_size = 5 * 1024 * 1024  # 5MB en bytes
    if value.size > max_size:
        raise ValidationError(
            'La taille du fichier ne doit pas dépasser 5MB',
            code='file_too_large'
        )


def validate_photo_format(value):
    """
    Valide le format du fichier photo.
    Formats acceptés: JPEG, PNG
    """
    valid_extensions = ['.jpg', '.jpeg', '.png']
    import os
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            'Format de fichier invalide. Utilisez JPEG ou PNG',
            code='invalid_format'
        )


# ============================================================================
# FORMULAIRES D'AUTHENTIFICATION
# ============================================================================

class PhoneRegistrationForm(forms.Form):
    """
    Formulaire d'inscription avec numéro de téléphone et mot de passe.
    Valide le format camerounais (+237XXXXXXXXX).
    """
    telephone = forms.CharField(
        max_length=20,
        validators=[validate_cameroon_phone],
        widget=TailwindTextInput(placeholder='+237683793777 ou 683793777'),
        label='Numéro de téléphone',
        help_text='Format: +237683793777 ou 683793777'
    )
    
    password = forms.CharField(
        min_length=6,
        widget=TailwindPasswordInput(placeholder='Minimum 6 caractères'),
        label='Mot de passe',
        help_text='Minimum 6 caractères'
    )
    
    password_confirm = forms.CharField(
        widget=TailwindPasswordInput(placeholder='Confirmez le mot de passe'),
        label='Confirmer le mot de passe'
    )
    
    def clean_telephone(self):
        """Normalise et valide le numéro de téléphone"""
        telephone = self.cleaned_data.get('telephone', '').strip()
        
        # Normalisation intelligente vers le format +237XXXXXXXXX
        if telephone:
            # Retirer tous les espaces et caractères spéciaux sauf +
            telephone = re.sub(r'[^\d+]', '', telephone)
            
            # Normaliser vers +237XXXXXXXXX
            if telephone.startswith('+237'):
                # Déjà au bon format
                pass
            elif telephone.startswith('237'):
                # Ajouter le +
                telephone = '+' + telephone
            elif telephone.startswith('6') and len(telephone) == 9:
                # Format court: ajouter +237
                telephone = '+237' + telephone
            else:
                # Format invalide
                raise ValidationError(
                    'Format invalide. Utilisez: +237683793777 ou 683793777',
                    code='invalid_phone'
                )
        
        # Vérifier si le numéro existe déjà
        if Membre.objects.filter(telephone=telephone).exists():
            raise ValidationError(
                'Ce numéro de téléphone est déjà enregistré',
                code='phone_exists'
            )
        
        return telephone
    
    def clean(self):
        """Valide que les deux mots de passe correspondent"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError(
                'Les deux mots de passe ne correspondent pas',
                code='password_mismatch'
            )
        
        return cleaned_data


class OTPVerificationForm(forms.Form):
    """
    Formulaire de vérification du code OTP.
    Accepte uniquement 6 chiffres.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[validate_otp_code],
        widget=TailwindTextInput(
            attrs={
                'maxlength': '6',
                'pattern': '[0-9]{6}',
                'inputmode': 'numeric',
                'autocomplete': 'one-time-code'
            },
            placeholder='000000'
        ),
        label='Code OTP',
        help_text='Entrez le code à 6 chiffres reçu par SMS'
    )
    
    def clean_code(self):
        """Valide que le code contient uniquement des chiffres"""
        code = self.cleaned_data.get('code')
        if code and not code.isdigit():
            raise ValidationError(
                'Le code doit contenir uniquement des chiffres',
                code='non_numeric'
            )
        return code


class LoginForm(AuthenticationForm):
    """
    Formulaire de connexion avec téléphone et mot de passe.
    Hérite de AuthenticationForm pour utiliser l'authentification Django.
    """
    username = forms.CharField(
        max_length=20,
        validators=[validate_cameroon_phone],
        widget=TailwindTextInput(placeholder='+237683793777 ou 683793777'),
        label='Numéro de téléphone'
    )
    
    password = forms.CharField(
        widget=TailwindPasswordInput(placeholder='Mot de passe'),
        label='Mot de passe'
    )
    
    def clean_username(self):
        """Normalise le numéro de téléphone"""
        username = self.cleaned_data.get('username', '').strip()
        
        # Normalisation intelligente vers le format +237XXXXXXXXX
        if username:
            # Retirer tous les espaces et caractères spéciaux sauf +
            username = re.sub(r'[^\d+]', '', username)
            
            # Normaliser vers +237XXXXXXXXX
            if username.startswith('+237'):
                # Déjà au bon format
                pass
            elif username.startswith('237'):
                # Ajouter le +
                username = '+' + username
            elif username.startswith('6') and len(username) == 9:
                # Format court: ajouter +237
                username = '+237' + username
        
        return username


# ============================================================================
# FORMULAIRE DE PROFIL
# ============================================================================

class ProfileForm(forms.ModelForm):
    """
    Formulaire de mise à jour du profil utilisateur.
    Gère nom, photo, ville et quartier.
    """
    
    # Liste des villes camerounaises principales
    VILLES_CAMEROUN = [
        ('', 'Sélectionnez une ville'),
        ('Yaoundé', 'Yaoundé'),
        ('Douala', 'Douala'),
        ('Garoua', 'Garoua'),
        ('Bafoussam', 'Bafoussam'),
        ('Bamenda', 'Bamenda'),
        ('Maroua', 'Maroua'),
        ('Ngaoundéré', 'Ngaoundéré'),
        ('Bertoua', 'Bertoua'),
        ('Limbé', 'Limbé'),
        ('Kribi', 'Kribi'),
        ('Edéa', 'Edéa'),
        ('Kumba', 'Kumba'),
        ('Nkongsamba', 'Nkongsamba'),
        ('Ebolowa', 'Ebolowa'),
        ('Buéa', 'Buéa'),
    ]
    
    ville = forms.ChoiceField(
        choices=VILLES_CAMEROUN,
        required=False,
        widget=TailwindSelect(),
        label='Ville'
    )
    
    class Meta:
        model = Membre
        fields = ['first_name', 'last_name', 'photo_profil', 'ville', 'quartier']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'photo_profil': 'Photo de profil',
            'ville': 'Ville',
            'quartier': 'Quartier'
        }
        widgets = {
            'first_name': TailwindTextInput(placeholder='Votre prénom'),
            'last_name': TailwindTextInput(placeholder='Votre nom'),
            'photo_profil': TailwindFileInput(),
            'quartier': TailwindTextInput(placeholder='Votre quartier'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs nom et prénom obligatoires
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
    
    def clean_photo_profil(self):
        """Valide le format et la taille de la photo"""
        photo = self.cleaned_data.get('photo_profil')
        
        if photo:
            # Valider le format
            validate_photo_format(photo)
            # Valider la taille
            validate_photo_size(photo)
        
        return photo
