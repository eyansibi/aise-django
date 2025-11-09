from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from .forms import UserRegisterForm
User = get_user_model()

def home(request):
    return render(request, 'frontoffice/home/home.html')

def contact_view(request):
    return render(request, 'frontoffice/contact.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé.")
            return redirect('home')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = UserRegisterForm()
    return render(request, 'frontoffice/users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
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

@staff_member_required
def backoffice_user_add(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur ajouté.")
            return redirect('backoffice_users')
    else:
        form = UserCreationForm()
    return render(request, 'backoffice/user_form.html', {'form': form})

@staff_member_required
def backoffice_user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Simplifié : réutilise UserCreationForm uniquement pour l'exemple.
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Modifications enregistrées (à implémenter).")
            return redirect('backoffice_users')
    else:
        form = UserCreationForm()
    return render(request, 'backoffice/user_form.html', {'form': form, 'user_obj': user})

@staff_member_required
def backoffice_user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé.")
        return redirect('backoffice_users')
    return render(request, 'backoffice/user_confirm_delete.html', {'user_obj': user})