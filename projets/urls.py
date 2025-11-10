# projets/urls.py
from django.urls import path
from . import views

app_name = 'projets'

urlpatterns = [
    path('backoffice/projets/', views.backoffice_projets, name='backoffice_projets'),
    path('backoffice/projets/add/', views.backoffice_projet_add, name='backoffice_projet_add'),
    path('backoffice/projets/edit/<int:projet_id>/', views.backoffice_projet_edit, name='backoffice_projet_edit'),
    path('backoffice/projets/delete/<int:projet_id>/', views.backoffice_projet_delete, name='backoffice_projet_delete'),

    # === Frontoffice (public) ===
    path('public/', views.projets_list_public, name='projets_public'),
    path('public/<int:projet_id>/', views.projet_detail_public, name='projet_detail_public'),
    path('generate-description/', views.generate_projet_description, name='generate_description'),

    
]