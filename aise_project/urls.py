# aise_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
# Import des vues publiques (home, contact)
from users import views as user_views
urlpatterns = [
    path('admin/', admin.site.urls),

    # === FrontOffice (vues publiques) ===
   # === FrontOffice ===
    path('', user_views.home, name='home'),                    # Page d'accueil
    path('home/', RedirectView.as_view(url='/')),              # ← Redirection /home → /
    path('contact/', user_views.contact_view, name='contact'),

    # === Users App (auth + backoffice) ===
    path('', include('users.urls')),  # Inclut tout : register, login, backoffice...

    # === Autres apps ===

    # === Projets App (backoffice) ===
    path('projets/', include('projets.urls')),
      
    path('blogs/', include('blogs.urls')), 
    
    path('reclamations/', include('reclamations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)