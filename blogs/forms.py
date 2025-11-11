# blogs/forms.py
from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['titre', 'contenu', 'categorie', 'image']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 12}),
            'categorie': forms.Select(attrs={'class': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style commun
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-sm'
                })
        # Image
        self.fields['image'].widget.attrs.update({
            'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none'
        })
        # Titre
        self.fields['titre'].widget.attrs.update({'placeholder': 'Ex: Comment l\'IA révolutionne la com institutionnelle'})
        # Contenu
        self.fields['contenu'].widget.attrs.update({'placeholder': 'Rédigez votre article ici...'})