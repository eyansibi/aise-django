# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()  # ← IMPORTANT : récupère ton User personnalisé


# === FORMULAIRE D'INSCRIPTION (frontoffice) ===
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition',
            'placeholder': 'Votre email'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition',
            'placeholder': 'Votre nom complet'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'nom', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition',
                'placeholder': {
                    'username': "Nom d'utilisateur",
                    'password1': 'Mot de passe',
                    'password2': 'Confirmer le mot de passe'
                }[field_name]
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nom = self.cleaned_data['nom']
        if commit:
            user.save()
        return user


# === FORMULAIRE DE CONNEXION ===
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-green-500 focus:outline-none transition',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-green-500 focus:outline-none transition',
            'placeholder': 'Mot de passe'
        })
    )


# === CRUD BACKOFFICE : AJOUT ===
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nom = forms.CharField(max_length=100, required=True)
    is_staff = forms.BooleanField(required=False, label="Administrateur")

    class Meta:
        model = User
        fields = ('username', 'nom', 'email', 'is_staff', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nom = self.cleaned_data['nom']
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
        return user


# === CRUD BACKOFFICE : ÉDITION ===
class CustomUserChangeForm(UserChangeForm):
    password = None  # Pas de mot de passe

    class Meta:
        model = User
        fields = ('username', 'nom', 'email', 'is_staff')