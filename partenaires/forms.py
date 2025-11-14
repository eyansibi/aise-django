# partenaires/forms.py
from django import forms
from .models import Partenaire

class PartenaireForm(forms.ModelForm):
    class Meta:
        model = Partenaire
        fields = ['nom', 'logo', 'site_web', 'description', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'Nom du partenaire'}),
            'site_web': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'placeholder': 'https://exemple.com'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'rows': 4, 'placeholder': 'Description...'}),
            'actif': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600'}),
        }
        labels = {
            'nom': 'Nom du partenaire',
            'logo': 'Logo',
            'site_web': 'Site web',
            'description': 'Description',
            'actif': 'Actif',
        }