# reclamations/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Reclamation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('traite', 'Traité'),
        ('rejete', 'Rejeté'),
    ]

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_reception = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    reponse = models.TextField(blank=True, null=True)
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reclamations_traitees')

    class Meta:
        ordering = ['-date_reception']
        verbose_name = 'Réclamation'
        verbose_name_plural = 'Réclamations'

    def __str__(self):
        return f"{self.sujet} - {self.nom}"