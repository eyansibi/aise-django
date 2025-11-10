# projets/resources.py
from import_export import resources
from .models import Projet

class ProjetResource(resources.ModelResource):
    class Meta:
        model = Projet
        fields = ('id', 'titre', 'description', 'statut', 'date_creation', 'createur__username')
        export_order = ('id', 'titre', 'statut', 'date_creation', 'createur__username')