from django.contrib import admin
from .models import Partenaire
from import_export.admin import ImportExportModelAdmin

@admin.register(Partenaire)
class PartenaireAdmin(ImportExportModelAdmin):
    list_display = ('nom', 'site_web', 'actif', 'date_ajout')
    list_filter = ('actif', 'date_ajout')
    search_fields = ('nom', 'description')
