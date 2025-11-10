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
from dateutil.relativedelta import relativedelta  # Ajout pour mois précis
from projets.models import Projet
from blogs.models import Blog
from reclamations.models import Reclamation

User = get_user_model()

import json

def home(request):
    return render(request, 'frontoffice/home/home.html')

def contact_view(request):
    return render(request, 'frontoffice/contact.html')

@staff_member_required(login_url='users:login')
def backoffice_dashboard(request):
    today = timezone.now().date()
    last_month = today - relativedelta(months=1)  # Mois précis
    last_6_months = [(today - relativedelta(months=i)) for i in range(6)][::-1]

    # === STATS SÉCURISÉES (gère None) ===
    total_users = User.objects.count()
    users_this_month = User.objects.filter(
        date_joined__date__gte=last_month
    ).count() if User.objects.filter(date_joined__isnull=False).exists() else 0
    # Calcul de croissance plus robuste
    if total_users == 0:
        users_growth = "+100%"
    else:
        growth_rate = (users_this_month / total_users * 100)
        users_growth = f"+{round(growth_rate, 1)}%"

    projets_actifs = Projet.objects.exclude(statut='termine').count()
    nouveaux_projets = Projet.objects.filter(
        date_creation__date__gte=last_month,
        date_creation__isnull=False
    ).count()

    total_reclamations = Reclamation.objects.count()
    reclamations_en_attente = Reclamation.objects.filter(statut='en_attente').count()

    total_blogs = Blog.objects.count()
    blogs_this_month = Blog.objects.filter(
        date_publication__date__gte=last_month,
        date_publication__isnull=False
    ).count()

    # === GRAPHIQUES ===
    # 1. Utilisateurs par mois
    users_labels, users_data = [], []
    for month in last_6_months:
        start = month.replace(day=1)
        end = (start + relativedelta(months=1) - relativedelta(days=1))  # Fin de mois précis
        count = User.objects.filter(
            date_joined__date__gte=start,
            date_joined__date__lte=end
        ).count()
        users_labels.append(start.strftime("%b %Y"))
        users_data.append(count)

    # 2. Projets par statut
    projets_status = Projet.objects.values('statut').annotate(count=Count('id'))
    projets_labels = [dict(Projet.STATUT_CHOICES).get(s['statut'], s['statut']) for s in projets_status]
    projets_data = [s['count'] for s in projets_status]

    # 3. Réclamations par mois
    reclamations_labels, reclamations_data = [], []
    for month in last_6_months:
        start = month.replace(day=1)
        end = (start + relativedelta(months=1) - relativedelta(days=1))
        count = Reclamation.objects.filter(
            date_reception__date__gte=start,
            date_reception__date__lte=end,
            date_reception__isnull=False
        ).count()
        reclamations_labels.append(start.strftime("%b %Y"))
        reclamations_data.append(count)

    # 4. Blogs par mois
    blogs_labels, blogs_data = [], []
    for month in last_6_months:
        start = month.replace(day=1)
        end = (start + relativedelta(months=1) - relativedelta(days=1))
        count = Blog.objects.filter(
            date_publication__date__gte=start,
            date_publication__date__lte=end,
            date_publication__isnull=False
        ).count()
        blogs_labels.append(start.strftime("%b %Y"))
        blogs_data.append(count)

    # === ACTIVITÉ RÉCENTE (corrigée avec timestamps pour tri) ===
    recent_activity = []

    # Derniers utilisateurs
    for u in User.objects.order_by('-date_joined')[:3]:
        dt = u.date_joined
        time = dt.strftime("%Hh%M") if dt else "inconnu"
        timestamp = dt.isoformat() if dt else '9999-12-31T00:00:00'  # Timestamp pour tri (vieux si None)
        recent_activity.append({
            'icon': 'fa-user-plus', 'color': 'text-green-500',
            'text': f"Nouvel admin <strong>{u.username}</strong> ajouté",
            'time': time,
            'timestamp': timestamp
        })

    # Derniers projets
    for p in Projet.objects.order_by('-date_modification')[:2]:
        dt = p.date_modification
        time = dt.strftime("%Hh%M") if dt else "inconnu"
        timestamp = dt.isoformat() if dt else '9999-12-31T00:00:00'
        recent_activity.append({
            'icon': 'fa-edit', 'color': 'text-blue-500',
            'text': f"Projet <strong>{p.titre}</strong> mis à jour",
            'time': time,
            'timestamp': timestamp
        })

    # Dernières réclamations
    for r in Reclamation.objects.order_by('-date_reception')[:2]:
        dt = r.date_reception
        time = dt.strftime("%Hh%M") if dt else "inconnu"
        timestamp = dt.isoformat() if dt else '9999-12-31T00:00:00'
        recent_activity.append({
            'icon': 'fa-envelope', 'color': 'text-orange-500',
            'text': f"Réclamation : <strong>{r.sujet}</strong>",
            'time': time,
            'timestamp': timestamp
        })

    # Tri correct par timestamp (plus récent en premier)
    recent_activity = sorted(recent_activity, key=lambda x: x['timestamp'], reverse=True)[:5]

    # === CONTEXTE ===
    context = {
        'total_users': total_users,
        'users_growth': users_growth,
        'projets_actifs': projets_actifs,
        'nouveaux_projets': f"+{nouveaux_projets}",
        'total_reclamations': total_reclamations,
        'reclamations_en_attente': reclamations_en_attente,
        'total_blogs': total_blogs,
        'blogs_this_month': f"+{blogs_this_month}",
        'recent_activity': recent_activity,

        # Graphiques (JSON safe)
        'users_chart': {'labels': json.dumps(users_labels), 'data': json.dumps(users_data)},
        'projets_chart': {'labels': json.dumps(projets_labels), 'data': json.dumps(projets_data)},
        'reclamations_chart': {'labels': json.dumps(reclamations_labels), 'data': json.dumps(reclamations_data)},
        'blogs_chart': {'labels': json.dumps(blogs_labels), 'data': json.dumps(blogs_data)},
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