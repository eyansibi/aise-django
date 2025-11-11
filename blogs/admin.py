from django.contrib import admin

# Register your models here.
# blogs/admin.py
from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'auteur', 'date_publication']
    list_filter = ['categorie', 'date_publication']
    search_fields = ['titre', 'contenu']
    readonly_fields = ['date_publication', 'auteur']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)