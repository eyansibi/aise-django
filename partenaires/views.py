# partenaires/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Partenaire
from .forms import PartenaireForm

# === BACKOFFICE ===

@staff_member_required(login_url='users:login')
def backoffice_partenaires(request):
    partenaires = Partenaire.objects.all().order_by('-date_ajout')
    return render(request, 'backoffice/partenaires/partenaire_list.html', {
        'partenaires': partenaires
    })

@staff_member_required(login_url='users:login')
def backoffice_partenaire_add(request):
    if request.method == 'POST':
        form = PartenaireForm(request.POST, request.FILES)
        if form.is_valid():
            partenaire = form.save()
            messages.success(request, f"Partenaire '{partenaire.nom}' ajouté avec succès.")
            return redirect('partenaires:backoffice_partenaires')
    else:
        form = PartenaireForm()
    return render(request, 'backoffice/partenaires/partenaire_form.html', {
        'form': form,
        'title': 'Ajouter un partenaire'
    })

@staff_member_required(login_url='users:login')
def backoffice_partenaire_edit(request, partenaire_id):
    partenaire = get_object_or_404(Partenaire, pk=partenaire_id)
    if request.method == 'POST':
        form = PartenaireForm(request.POST, request.FILES, instance=partenaire)
        if form.is_valid():
            form.save()
            messages.success(request, f"Partenaire '{partenaire.nom}' modifié avec succès.")
            return redirect('partenaires:backoffice_partenaires')
    else:
        form = PartenaireForm(instance=partenaire)
    return render(request, 'backoffice/partenaires/partenaire_form.html', {
        'form': form,
        'title': 'Modifier le partenaire',
        'partenaire': partenaire
    })

@staff_member_required(login_url='users:login')
def backoffice_partenaire_delete(request, partenaire_id):
    partenaire = get_object_or_404(Partenaire, pk=partenaire_id)
    if request.method == 'POST':
        nom = partenaire.nom
        partenaire.delete()
        messages.success(request, f"Partenaire '{nom}' supprimé avec succès.")
        return redirect('partenaires:backoffice_partenaires')
    return render(request, 'backoffice/partenaires/partenaire_confirm_delete.html', {
        'partenaire': partenaire
    })

# === FRONTOFFICE ===
def partenaires_public(request):
    partenaires = Partenaire.objects.filter(actif=True).order_by('?')[:10]  # 10 max, aléatoire ou trié
    return render(request, 'frontoffice/partenaires/partenaires_slider.html', {
        'partenaires': partenaires
    })