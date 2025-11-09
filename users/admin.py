from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin simplifié pour AISE"""
    
    list_display = ['username', 'email', 'nom', 'role', 'date_inscription']
    list_filter = ['role', 'date_inscription', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'nom']
    ordering = ['-date_inscription']
    
    fieldsets = (
        ('Connexion', {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'email')}),
        ('Rôle', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Dates', {'fields': ('last_login','date_joined','date_inscription')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email','nom','role','password1','password2'),
        }),
    )
