# projets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.http import urlencode
from .models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = [
        'admin_image',
        'titre',
        'statut_badge',
        'createur_link',
        'date_creation_formatted',
        'actions_column',
    ]

    list_filter = ['statut', 'date_creation', 'createur']
    search_fields = [
        'titre__icontains',
        'description__icontains',
        'createur__username__icontains',
        'createur__email__icontains',
    ]
    readonly_fields = ['date_creation', 'date_modification', 'createur']
    ordering = ['-date_creation']
    date_hierarchy = 'date_creation'
    list_per_page = 25

    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'image', 'admin_image_preview')
        }),
        ('Métadonnées', {
            'fields': ('statut', 'createur', 'date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )

    actions = ['marquer_comme_termine', 'marquer_comme_en_cours']

    def marquer_comme_termine(self, request, queryset):
        updated = queryset.update(statut='termine')
        self.message_user(request, f"{updated} projet(s) marqué(s) comme terminé(s).")
    marquer_comme_termine.short_description = "Marquer comme terminé"

    def marquer_comme_en_cours(self, request, queryset):
        updated = queryset.update(statut='en_cours')
        self.message_user(request, f"{updated} projet(s) marqué(s) comme en cours.")
    marquer_comme_en_cours.short_description = "Marquer comme en cours"

    # === AFFICHAGE ===
    def admin_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 50px; width: auto; border-radius: 6px; object-fit: cover;" />',
                obj.image.url
            )
        return format_html('<span class="text-gray-400 text-xs">Aucune</span>')
    admin_image.short_description = 'Image'

    def admin_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; width: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Aucune image"
    admin_image_preview.short_description = 'Aperçu'

    def statut_badge(self, obj):
        colors = {
            'en_cours': 'bg-blue-100 text-blue-800',
            'termine': 'bg-green-100 text-green-800',
            'en_attente': 'bg-yellow-100 text-yellow-800',
            'annule': 'bg-red-100 text-red-800',
        }
        color = colors.get(obj.statut, 'bg-gray-100 text-gray-800')
        label = dict(obj.STATUT_CHOICES).get(obj.statut, obj.statut)
        return format_html(
            '<span class="px-3 py-1 rounded-full text-xs font-medium {}">{}</span>',
            color, label
        )
    statut_badge.short_description = 'Statut'

    def createur_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.createur.id])
        return format_html(
            '<a href="{}" class="text-blue-600 hover:underline">{}</a>',
            url, obj.createur.get_full_name() or obj.createur.username
        )
    createur_link.short_description = 'Créateur'

    def date_creation_formatted(self, obj):
        return obj.date_creation.strftime("%d/%m/%Y %H:%M")
    date_creation_formatted.short_description = 'Créé le'

    def actions_column(self, obj):
        detail_url = reverse('projets:projet_detail_public', args=[obj.pk])
        edit_url = reverse('projets:backoffice_projet_edit', args=[obj.pk])
        return format_html(
            '''
            <div class="flex gap-2">
                <a href="{}" target="_blank" class="text-green-600 hover:text-green-800 text-xs" title="Voir public">
                    <i class="fas fa-eye"></i>
                </a>
                <a href="{}" class="text-blue-600 hover:text-blue-800 text-xs" title="Modifier">
                    <i class="fas fa-edit"></i>
                </a>
            </div>
            ''',
            detail_url, edit_url
        )
    actions_column.short_description = 'Actions'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('createur')

    # === PDF EXPORT ===
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-pdf/', self.admin_site.admin_view(self.export_pdf_view), name='projets_export_pdf'),
        ]
        return custom_urls + urls

    def export_pdf_view(self, request):
        from .views import export_projets_pdf
        return export_projets_pdf(request)

    def pdf_export_link(self, obj=None):
        if obj is None:
            url = reverse('admin:projets_export_pdf')
            return format_html(
                '<a href="{}" class="button" style="background:#087065;color:white;padding:8px 16px;border-radius:6px;font-size:13px;">'
                '<i class="fas fa-file-pdf"></i> Exporter PDF</a>',
                url
            )
        return ""
    pdf_export_link.short_description = "PDF"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['extra_buttons'] = self.pdf_export_link()
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {'all': ('admin/css/projet_admin.css',)}