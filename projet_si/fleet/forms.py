from django import forms
from .models import *

class ChauffeurForm(forms.ModelForm):
    class Meta:
        model = Chauffeur
        fields = '__all__'

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = '__all__'


class TourneeForm(forms.ModelForm):
    class Meta:
        model = Tournee
        fields = ['date_tournee', 'chauffeur', 'vehicule']
        widgets = {
            'date_tournee': forms.DateInput(
                attrs={'type': 'date'}
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        chauffeur = cleaned_data.get('chauffeur')

        if chauffeur and not chauffeur.disponibilite:
            raise forms.ValidationError("This driver is not available.")

        return cleaned_data
    

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

