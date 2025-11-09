from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Modèle utilisateur simplifié pour AISE"""
    
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Client', 'Client'),
        ('Visiteur', 'Visiteur'),
    ]
    
    # Nom complet
    nom = models.CharField(max_length=100, verbose_name="Nom", blank=True)
    
    # Rôle
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Visiteur',
        verbose_name="Rôle"
    )
    
    # Profil simple (optionnel)
    bio = models.TextField(blank=True, verbose_name="Biographie")
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        verbose_name="Avatar"
    )
    
    # Dates
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
