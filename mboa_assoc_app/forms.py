from django import forms
from .models import Paiement, MethodePaiementModel

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['cotisation', 'membre', 'montant', 'methode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les choix de méthode aux valeurs définies
        self.fields['methode'].queryset = MethodePaiementModel.objects.all()
