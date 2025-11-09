# projets/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Projet
from .forms import ProjetForm

@staff_member_required(login_url='users:login')
def backoffice_projets(request):
    projets = Projet.objects.all()
    return render(request, 'backoffice/projets/projets_list.html', {'projets': projets})

@staff_member_required(login_url='users:login')
def backoffice_projet_add(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST,request.FILES)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.createur = request.user
            projet.save()
            messages.success(request, f"Projet '{projet.titre}' ajouté.")
            return redirect('projets:backoffice_projets')
    else:
        form = ProjetForm()
    return render(request, 'backoffice/projets/projet_form.html', {
        'form': form,
        'title': 'Ajouter un projet'
    })

@staff_member_required(login_url='users:login')
def backoffice_projet_edit(request, projet_id):
    projet = get_object_or_404(Projet, pk=projet_id)
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, f"Projet '{projet.titre}' modifié.")
            return redirect('projets:backoffice_projets')
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'backoffice/projets/projet_form.html', {
        'form': form,
        'title': 'Modifier le projet'
    })

@staff_member_required(login_url='users:login')
def backoffice_projet_delete(request, projet_id):
    projet = get_object_or_404(Projet, pk=projet_id)
    
    if request.method == 'POST':
        titre = projet.titre
        projet.delete()
        messages.success(request, f"Projet '{titre}' supprimé.")
        return redirect('projets:backoffice_projets')

    return render(request, 'backoffice/projets/projet_confirm_delete.html', {
        'projet': projet
    })


# === FRONTOFFICE ===
def projets_list_public(request):
    projets = Projet.objects.filter(statut='termine').order_by('-date_creation')
    return render(request, 'frontoffice/projets/projets_list.html', {
        'projets': projets,
        'page_title': 'Nos Projets'
    })

def projet_detail_public(request, projet_id):
    projet = get_object_or_404(Projet, pk=projet_id, statut='termine')
    return render(request, 'frontoffice/projets/projet_detail.html', {
        'projet': projet,
        'page_title': projet.titre
    })