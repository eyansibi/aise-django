from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserRegisterForm
from .forms import CustomUserCreationForm, CustomUserChangeForm
User = get_user_model()

def home(request):
    return render(request, 'frontoffice/home/home.html')

def contact_view(request):
    return render(request, 'frontoffice/contact.html')

@staff_member_required
def backoffice_dashboard(request):
    return render(request, 'backoffice/dashboard.html')

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
def backoffice_dashboard(request):
    return render(request, 'backoffice/dashboard.html')

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