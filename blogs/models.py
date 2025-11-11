# blogs/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# === CHOIX DE CATÉGORIES (modifiable) ===
CATEGORIES = [
    ('strategie', 'Stratégie'),
    ('ia', 'IA & Communication'),
    ('institutionnel', 'Institutionnel'),
    ('evenement', 'Événementiel'),
    ('autre', 'Autre'),
]

class Blog(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    categorie = models.CharField(
        max_length=50,
        choices=CATEGORIES,
        default='autre',
        verbose_name="Catégorie"
    )
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    date_publication = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')

    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.titre

    def get_categorie_display_fr(self):
        """Retourne le libellé en français"""
        return dict(CATEGORIES).get(self.categorie, self.categorie)