# partenaires/urls.py
from django.urls import path
from . import views

app_name = 'partenaires'

urlpatterns = [
    # Backoffice
    path('backoffice/', views.backoffice_partenaires, name='backoffice_partenaires'),
    path('backoffice/ajouter/', views.backoffice_partenaire_add, name='backoffice_partenaire_add'),
    path('backoffice/<int:partenaire_id>/modifier/', views.backoffice_partenaire_edit, name='backoffice_partenaire_edit'),
    path('backoffice/<int:partenaire_id>/supprimer/', views.backoffice_partenaire_delete, name='backoffice_partenaire_delete'),
]