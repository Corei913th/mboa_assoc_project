from django import forms
from django.core.exceptions import ValidationError
from .models import Association, Adhesion, Membre


class AssociationForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier une association
    """
    
    class Meta:
        model = Association
        fields = [
            'name', 
            'type', 
            'description', 
            'registration_number',
            'legal_status',
            'creation_date',
            'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nom de l\'association'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Décrivez votre association...',
                'rows': 4
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Numéro d\'enregistrement (optionnel)'
            }),
            'legal_status': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Statut juridique (optionnel)'
            }),
            'creation_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*'
            })
        }
    
    def clean_name(self):
        """Valide que le nom est unique et a au moins 3 caractères"""
        name = self.cleaned_data.get('name')
        
        if len(name) < 3:
            raise ValidationError("Le nom doit contenir au moins 3 caractères")
        
        # Vérifier l'unicité du nom (sauf pour la modification)
        qs = Association.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError("Une association avec ce nom existe déjà")
        
        return name
    
    def clean_logo(self):
        """Valide la taille et le type du logo"""
        logo = self.cleaned_data.get('logo')
        
        if logo:
            # Vérifier la taille (max 5MB)
            if logo.size > 5 * 1024 * 1024:
                raise ValidationError("Le logo ne doit pas dépasser 5MB")
            
            # Vérifier le type de fichier
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if logo.content_type not in allowed_types:
                raise ValidationError("Le logo doit être une image (JPEG, PNG ou GIF)")
        
        return logo
    
    def clean_registration_number(self):
        """Valide l'unicité du numéro d'enregistrement s'il est fourni"""
        reg_number = self.cleaned_data.get('registration_number')
        
        if reg_number:
            qs = Association.objects.filter(registration_number=reg_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError("Ce numéro d'enregistrement est déjà utilisé")
        
        return reg_number


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