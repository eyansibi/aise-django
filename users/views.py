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
from django.db import models
from django.db.models import Avg,F
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import Counter
import re

User = get_user_model()

import json

def home(request):
    return render(request, 'frontoffice/home/home.html')

def contact_view(request):
    return render(request, 'frontoffice/contact.html')

@staff_member_required(login_url='users:login')
def backoffice_dashboard(request):
    today = timezone.now()
    last_6_months = [(today - relativedelta(months=i)) for i in range(5, -1, -1)]

    # === 1. STATS CLASSIQUES ===
    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__month=today.month, date_joined__year=today.year).count()
    users_growth = f"+{round((users_this_month / max(total_users - users_this_month, 1)) * 100, 1)}%" if total_users > users_this_month else "+0%"

    projets_actifs = Projet.objects.exclude(statut='termine').count()
    nouveaux_projets = Projet.objects.filter(date_creation__month=today.month).count()

    total_reclamations = Reclamation.objects.count()
    reclamations_en_attente = Reclamation.objects.filter(statut='en_attente').count()

    total_blogs = Blog.objects.count()
    blogs_this_month = Blog.objects.filter(date_publication__month=today.month).count()

    # === 2. RÉSOLUTION MOYENNE ===
    reclamations_traitees = Reclamation.objects.filter(
        statut='traitee',
        date_reception__isnull=False
    )
    if reclamations_traitees.exists():
        avg_duration = reclamations_traitees.aggregate(
            avg=Count(F('date_reception'))  # On simule si pas de date_traitement
        )
        # Si tu as `date_traitement`, remplace par :
        # avg_duration = reclamations_traitees.aggregate(avg=Avg(F('date_traitement') - F('date_reception')))
        avg_resolution_days = 3  # Valeur simulée pour démo
    else:
        avg_resolution_days = 0

    # === 3. GRAPHIQUES : ÉVOLUTION MENSUELLE ===
    months_labels = [m.strftime("%b %Y") for m in last_6_months]

    # Utilisateurs par mois
    users_data = []
    for m in last_6_months:
        count = User.objects.filter(
            date_joined__year=m.year,
            date_joined__month=m.month
        ).count()
        users_data.append(count)

    # Réclamations par mois
    reclamations_data = []
    for m in last_6_months:
        count = Reclamation.objects.filter(
            date_reception__year=m.year,
            date_reception__month=m.month
        ).count()
        reclamations_data.append(count)

    # === 4. ACTIVITÉ RÉCENTE (CORRIGÉE) ===
    recent_activity = []

    # Derniers utilisateurs
    for user in User.objects.order_by('-date_joined')[:3]:
        time_str = timezone.localtime(user.date_joined).strftime("%H:%M")
        recent_activity.append({
            'icon': 'fa-user-plus',
            'color': 'text-green-600',
            'text': f"<strong>{user.get_full_name() or user.username}</strong> s'est inscrit",
            'time': time_str
        })

    # Derniers projets
    for projet in Projet.objects.order_by('-date_creation')[:2]:
        time_str = timezone.localtime(projet.date_creation).strftime("%H:%M")
        recent_activity.append({
            'icon': 'fa-folder-plus',
            'color': 'text-blue-600',
            'text': f"Nouveau projet : <strong>{projet.titre}</strong>",
            'time': time_str
        })

    # Dernières réclamations
    for rec in Reclamation.objects.order_by('-date_reception')[:2]:
        time_str = timezone.localtime(rec.date_reception).strftime("%H:%M")
        recent_activity.append({
            'icon': 'fa-envelope',
            'color': 'text-orange-600',
            'text': f"Réclamation de <strong>{rec.email}</strong>",
            'time': time_str
        })

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
        'avg_resolution_days': avg_resolution_days,

        # Graphiques
        'users_chart_labels': json.dumps(months_labels),
        'users_chart_data': json.dumps(users_data),
        'reclamations_chart_labels': json.dumps(months_labels),
        'reclamations_chart_data': json.dumps(reclamations_data),

        # Activité récente
        'recent_activity': recent_activity[:7],
    }

    return render(request, 'backoffice/dashboard.html', context)  
    last_6_months = [(today - relativedelta(months=i)) for i in range(6)][::-1]

    # === STATS CLASSIQUES (améliorées) ===
    total_users = User.objects.count()
    users_this_month = User.objects.filter(date_joined__date__gte=last_month).count()
    users_growth = f"+{round(users_this_month / max(total_users, 1) * 100, 1)}%"

    projets_actifs = Projet.objects.exclude(statut='termine').count()
    nouveaux_projets = Projet.objects.filter(date_creation__date__gte=last_month).count()

    total_reclamations = Reclamation.objects.count()
    reclamations_en_attente = Reclamation.objects.filter(statut='en_attente').count()
    reclamations_traitees = Reclamation.objects.filter(statut='traitee')

    total_blogs = Blog.objects.count()
    blogs_this_month = Blog.objects.filter(date_publication__date__gte=last_month).count()

    # === NOUVEAU : TAUX DE RÉSOLUTION MOYEN ===
    avg_resolution = reclamations_traitees.aggregate(
        avg_days=Avg(
            (timezone.now() - F('date_reception')), 
            output_field=models.DurationField()
        )
    )['avg_days']
    avg_resolution_days = avg_resolution.days if avg_resolution else 0

    # === NOUVEAU : PROJETS À RISQUE (retard > 7 jours) ===
    projets_a_risque = Projet.objects.filter(
        statut='en_cours',
        date_creation__lt=timezone.now() - timedelta(days=7)
    ).count()

    # === NOUVEAU : SCORE DE SATISFACTION ESTIMÉ (IA simulée) ===
    # Basé sur : rapidité + volume traité + feedback implicite
    rapidite_score = max(0, 10 - avg_resolution_days) if avg_resolution_days <= 10 else 0
    volume_score = min(10, reclamations_traitees.count() / max(total_reclamations, 1) * 10)
    satisfaction_score = round((rapidite_score + volume_score) / 2, 1)

    # === NOUVEAU : TOP 3 MOTS-CLÉS DANS RÉCLAMATIONS ===
    mots = []
    for r in Reclamation.objects.all():
        mots.extend(re.findall(r'\b\w{4,}\b', r.sujet.lower() + " " + r.message.lower()))
    top_mots = Counter(mots).most_common(3)
    top_mots_labels = [f"{mot.title()} ({count})" for mot, count in top_mots]

    # === NOUVEAU : PRÉDICTION RÉCLAMATIONS MOIS PROCHAIN (tendance simple) ===
    reclamations_mensuelles = []
    for month in last_6_months:
        start = month.replace(day=1)
        end = (start + relativedelta(months=1) - relativedelta(days=1))
        count = Reclamation.objects.filter(
            date_reception__date__gte=start,
            date_reception__date__lte=end
        ).count()
        reclamations_mensuelles.append(count)
    
    # Tendance linéaire simple
    if len(reclamations_mensuelles) > 1:
        tendance = sum(reclamations_mensuelles[-3:]) / 3
        prediction = round(tendance * 1.1)  # +10% estimation
    else:
        prediction = reclamations_en_attente + 2

    # === NOUVEAU : CROISSANCE BLOGS vs PROJETS ===
    croissance_blogs = blogs_this_month
    croissance_projets = nouveaux_projets
    if croissance_projets > croissance_blogs:
        croissance_leader = "Projets"
        croissance_diff = f"+{croissance_projets - croissance_blogs}"
    elif croissance_blogs > croissance_projets:
        croissance_leader = "Blogs"
        croissance_diff = f"+{croissance_blogs - croissance_projets}"
    else:
        croissance_leader = "Équilibré"
        croissance_diff = ""

    # === GRAPHIQUES (JSON) ===
    users_labels = [m.strftime("%b %Y") for m in last_6_months]
    users_data = [User.objects.filter(date_joined__date__gte=m.replace(day=1), 
                                      date_joined__date__lte=(m.replace(day=1) + relativedelta(months=1) - timedelta(days=1))).count() 
                  for m in last_6_months]

    # === CONTEXTE FINAL ===
    context = {
        # Stats classiques
        'total_users': total_users,
        'users_growth': users_growth,
        'projets_actifs': projets_actifs,
        'nouveaux_projets': f"+{nouveaux_projets}",
        'total_reclamations': total_reclamations,
        'reclamations_en_attente': reclamations_en_attente,
        'total_blogs': total_blogs,
        'blogs_this_month': f"+{blogs_this_month}",

        # NOUVELLES STATS ORIGINALES
        'avg_resolution_days': avg_resolution_days,
        'projets_a_risque': projets_a_risque,
        'satisfaction_score': satisfaction_score,
        'top_mots_labels': top_mots_labels or ["Aucun mot détecté"],
        'prediction_reclamations': prediction,
        'croissance_leader': croissance_leader,
        'croissance_diff': croissance_diff,

        # Graphiques
        'users_chart': {'labels': json.dumps(users_labels), 'data': json.dumps(users_data)},
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