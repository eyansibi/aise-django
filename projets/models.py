# projets/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Projet(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('en_attente', 'En attente'),
        ('annule', 'Annulé'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    image = models.ImageField(upload_to='projets/', blank=True, null=True)  # ← NOUVEAU
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projets_crees')

    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'

    def __str__(self):
        return self.titre