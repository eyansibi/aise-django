# projets/mixins.py
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import ListView
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO


class SearchFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(titre__icontains=query) | Q(description__icontains=query)
            )
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset.order_by('-date_creation')


class ExportMixin:
    def export_csv(self, queryset, resource_class):
        resource = resource_class()
        dataset = resource.export(queryset)
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projets.csv"'
        return response

    def export_excel(self, queryset, resource_class):
        resource = resource_class()
        dataset = resource.export(queryset)
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="projets.xlsx"'
        return response

    def export_pdf(self, queryset):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Titre
        elements.append(Paragraph("Liste des Projets - AISE", styles['Title']))

        # Table
        data = [['ID', 'Titre', 'Statut', 'Créé le', 'Créateur']]
        for p in queryset:
            data.append([
                str(p.id),
                p.titre,
                p.get_statut_display(),
                p.date_creation.strftime('%d/%m/%Y'),
                p.createur.username
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="projets.pdf"'
        return response