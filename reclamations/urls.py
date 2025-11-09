# reclamations/urls.py
from django.urls import path
from . import views

app_name = 'reclamations'

urlpatterns = [
    # === Frontoffice ===
    path('signaler/', views.reclamation_public, name='reclamation_public'),

    # === Backoffice ===
    path('', views.backoffice_reclamations, name='backoffice_reclamations'),
    path('<int:reclamation_id>/', views.backoffice_reclamation_detail, name='backoffice_reclamation_detail'),
]