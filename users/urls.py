# users/urls.py
from django.urls import path
from . import views

app_name = 'users'  # Important pour les reverse() avec namespace

urlpatterns = [
    # === Authentification ===
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # === BackOffice (admin) ===
    path('backoffice/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('backoffice/users/', views.backoffice_users, name='backoffice_users'),
    path('backoffice/users/add/', views.backoffice_user_add, name='backoffice_user_add'),
    path('backoffice/users/edit/<int:user_id>/', views.backoffice_user_edit, name='backoffice_user_edit'),
    path('backoffice/users/delete/<int:user_id>/', views.backoffice_user_delete, name='backoffice_user_delete'),
]