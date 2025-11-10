from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserRegisterForm
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from projets.models import Projet
from blogs.models import Blog
from reclamations.models import Reclamation
User = get_user_model()

def home(request):
    return render(request, 'frontoffice/home/home.html')

def contact_view(request):
    return render(request, 'frontoffice/contact.html')

@staff_member_required(login_url='users:login')
def backoffice_dashboard(request):
    # === PÉRIODE (pour évolution) ===
    today = timezone.now().date()
    last_month = today - timedelta(days=30)

    # === STATS PRINCIPALES ===
    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__date__gte=last_month).count()
    users_growth = round((users_this_month / total_users * 100) if total_users > 0 else 0, 1)

    total_projets = Projet.objects.count()
    projets_actifs = Projet.objects.exclude(statut='termine').count()
    nouveaux_projets = Projet.objects.filter(date_creation__date__gte=last_month).count()

    total_reclamations = Reclamation.objects.count()
    reclamations_en_attente = Reclamation.objects.filter(statut='en_attente').count()

    total_blogs = Blog.objects.count()
    blogs_this_month = Blog.objects.filter(date_publication__date__gte=last_month).count()

    # === ACTIVITÉ RÉCENTE (3 derniers événements) ===
    recent_activity = []

    # Derniers utilisateurs
    last_users = User.objects.order_by('-date_joined')[:3]
    for u in last_users:
        recent_activity.append({
            'icon': 'fa-user-plus',
            'color': 'text-green-500',
            'text': f"Nouvel admin <strong>{u.username}</strong> ajouté",
            'time': u.date_joined.strftime("%Hh%M")
        })

    # Derniers projets modifiés
    last_projets = Projet.objects.order_by('-date_modification')[:2]
    for p in last_projets:
        recent_activity.append({
            'icon': 'fa-edit',
            'color': 'text-blue-500',
            'text': f"Projet <strong>#{p.id} {p.titre}</strong> mis à jour",
            'time': p.date_modification.strftime("%Hh%M")
        })

    # Dernières réclamations
    last_reclamations = Reclamation.objects.order_by('-date_reception')[:2]
    for r in last_reclamations:
        recent_activity.append({
            'icon': 'fa-envelope',
            'color': 'text-orange-500',
            'text': f"Nouvelle réclamation : <strong>{r.sujet}</strong>",
            'time': r.date_reception.strftime("%Hh%M")
        })

    # Trier par date
    recent_activity = sorted(recent_activity, key=lambda x: x['time'], reverse=True)[:5]

    # === CONTEXTE ===
    context = {
        'total_users': total_users,
        'users_growth': f"+{users_growth}%" if users_growth > 0 else "0%",
        'projets_actifs': projets_actifs,
        'nouveaux_projets': f"+{nouveaux_projets}",
        'reclamations_en_attente': reclamations_en_attente,
        'total_reclamations': total_reclamations,
        'total_blogs': total_blogs,
        'blogs_this_month': f"+{blogs_this_month}",
        'recent_activity': recent_activity,
    }
    return render(request, 'backoffice/dashboard.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue, {user.nom or user.username} !")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'frontoffice/users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:  # SEUL LES ADMINS
                login(request, user)
                return redirect('users:backoffice_dashboard')
            else:
                messages.error(request, "Accès réservé aux administrateurs.")
        else:
            messages.error(request, "Identifiants invalides.")
    else:
        form = AuthenticationForm()
    return render(request, 'frontoffice/users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@staff_member_required
def backoffice_users(request):
    users = User.objects.all()
    return render(request, 'backoffice/users_list.html', {'users': users})

@staff_member_required(login_url='users:login')
def backoffice_user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {form.cleaned_data['username']} ajouté.")
            return redirect('users:backoffice_users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'backoffice/user_form.html', {
        'form': form,
        'title': 'Ajouter un utilisateur'
    })

@staff_member_required(login_url='users:login')
def backoffice_user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {user.username} modifié.")
            return redirect('users:backoffice_users')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'backoffice/user_form.html', {
        'form': form,
        'title': 'Modifier l\'utilisateur',
        'user_obj': user
    })

@staff_member_required(login_url='users:login')
def backoffice_user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas vous supprimer vous-même.")
        return redirect('users:backoffice_users')  # CORRIGÉ

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Utilisateur {username} supprimé avec succès.")
        return redirect('users:backoffice_users')  # CORRIGÉ

    return render(request, 'backoffice/user_confirm_delete.html', {
        'user_obj': user
    })