from django.db import models
from django.utils import timezone

class Partenaire(models.Model):
    nom = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partenaires/', null=True, blank=True)
    site_web = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    date_ajout = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_ajout']
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.nom