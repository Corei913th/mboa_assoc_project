from django import forms
from django.core.exceptions import ValidationError
from .models import Association, Adhesion, Membre
import re


# ============================================================================
# VALIDATEURS
# ============================================================================

def validate_cameroon_phone(value):
    """Valide le format du numéro de téléphone camerounais"""
    pattern = r'^(\+?237)?[6][0-9]{8}$'
    if not re.match(pattern, value):
        raise ValidationError('Format invalide. Utilisez: +237683793777 ou 683793777')


def validate_otp_code(value):
    """Valide le format du code OTP (6 chiffres)"""
    if not re.match(r'^[0-9]{6}$', value):
        raise ValidationError('Le code OTP doit contenir exactement 6 chiffres')


# ============================================================================
# FORMULAIRES
# ============================================================================

class AssociationForm(forms.ModelForm):
    class Meta:
        model = Association
        fields = ['name', 'type', 'description', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom de l\'association'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Décrivez votre association...', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-file', 'accept': 'image/*'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Le nom doit contenir au moins 3 caractères")
        qs = Association.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Une association avec ce nom existe déjà")
        return name
    
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise ValidationError("Le logo ne doit pas dépasser 5MB")
            if logo.content_type not in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']:
                raise ValidationError("Format invalide. Utilisez JPEG, PNG ou GIF")
        return logo


class CotisationForm(forms.Form):
    type_cotisation = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Cotisation mensuelle'}),
        label='Type de cotisation'
    )
    montant = forms.DecimalField(
        min_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5000', 'step': '100'}),
        label='Montant (FCFA)'
    )
    date_echeance = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        label='Date d\'échéance'
    )


class InvitationForm(forms.Form):
    telephone = forms.CharField(
        max_length=20,
        validators=[validate_cameroon_phone],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+237683793777'}),
        label='Numéro de téléphone'
    )


class AddMemberForm(forms.Form):
    """
    Formulaire pour ajouter un membre à une association
    """
    user = forms.ModelChoiceField(
        queryset=Membre.objects.all(),
        label="Utilisateur",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, association=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclure les membres déjà dans l'association
        if association:
            existing_members = Adhesion.objects.filter(
                association=association
            ).values_list('membre_id', flat=True)
            
            self.fields['user'].queryset = Membre.objects.exclude(
                id__in=existing_members
            )


class NominatePresidentForm(forms.Form):
    """
    Formulaire pour nommer un nouveau président
    """
    new_president = forms.ModelChoiceField(
        queryset=None,
        label="Nouveau président",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, association=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Seuls les membres actuels peuvent être nommés
        if association:
            from .models import Role
            self.fields['new_president'].queryset = Membre.objects.filter(
                adhesions__association=association,
                adhesions__is_active=True
            ).exclude(
                adhesions__role=Role.PRESIDENT
            )


class NominateTreasurerForm(forms.Form):
    """
    Formulaire pour nommer un trésorier
    """
    treasurer = forms.ModelChoiceField(
        queryset=None,
        label="Trésorier",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    def __init__(self, *args, association=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Seuls les membres actuels peuvent être nommés
        if association:
            from .models import Role
            self.fields['treasurer'].queryset = Membre.objects.filter(
                adhesions__association=association,
                adhesions__is_active=True
            ).exclude(
                adhesions__role=Role.PRESIDENT
            )


class SearchMemberForm(forms.Form):
    """
    Formulaire pour rechercher des utilisateurs à ajouter
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        label="Rechercher un utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nom d\'utilisateur ou email...'
        })
    )


# ============================================================================
# WIDGETS TAILWIND POUR FORMULAIRES OTP
# ============================================================================

import re
from django.contrib.auth.forms import AuthenticationForm


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
    """Widget FileInput avec classes  réutilisables"""
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
# FORMULAIRES D'AUTHENTIFICATION OTP
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
