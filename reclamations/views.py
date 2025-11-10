from django.shortcuts import render

# Create your views here.
# reclamations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Reclamation
from .forms import ReclamationForm
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
import json
import logging
import re



logger = logging.getLogger(__name__)

# === FRONTOFFICE (public) ===
def reclamation_public(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save()
            messages.success(request, "Votre réclamation a été envoyée avec succès. Nous vous répondrons bientôt.")
            
            # Optionnel : envoi email
            try:
                send_mail(
                    subject=f"Nouvelle réclamation : {reclamation.sujet}",
                    message=f"""
                    De : {reclamation.nom} ({reclamation.email})
                    Sujet : {reclamation.sujet}
                    Message : {reclamation.message}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['admin@aise.com'],
                    fail_silently=True,
                )
            except:
                pass  # En prod, loguer l'erreur

            return redirect('reclamations:reclamation_public')
    else:
        form = ReclamationForm()
    return render(request, 'frontoffice/reclamation_form.html', {
        'form': form,
        'page_title': 'Signaler un problème'
    })

# === BACKOFFICE ===
@staff_member_required(login_url='users:login')
def backoffice_reclamations(request):
    reclamations = Reclamation.objects.all()
    return render(request, 'backoffice/reclamations/reclamations_list.html', {'reclamations': reclamations})

@staff_member_required(login_url='users:login')
def backoffice_reclamation_detail(request, reclamation_id):
    reclamation = get_object_or_404(Reclamation, pk=reclamation_id)
    
    if request.method == 'POST':
        statut = request.POST.get('statut')
        reponse = request.POST.get('reponse', '').strip()
        
        if statut in ['traite', 'rejete'] and reponse:
            reclamation.statut = statut
            reclamation.reponse = reponse
            reclamation.traite_par = request.user
            reclamation.date_traitement = timezone.now()
            reclamation.save()

            # ENVOI EMAIL
            sujet_email = f"[AISE] Réponse à votre réclamation : {reclamation.sujet}"
            corps = f"""
            Bonjour {reclamation.nom},

            Nous avons bien reçu votre réclamation du {reclamation.date_reception.strftime("%d/%m/%Y à %H:%M")}.

            **Statut :** {reclamation.get_statut_display().upper()}
            **Notre réponse :**

            {reponse}

            ---
            Merci pour votre confiance.
            Cordialement,
            L'équipe AISE
            contact@aise.tn
            """

            try:
                send_mail(
                    subject=sujet_email,
                    message=corps,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reclamation.email],
                    fail_silently=False,
                )
                messages.success(request, f"Réponse envoyée à {reclamation.email}")
            except Exception as e:
                messages.error(request, f"Réponse sauvegardée, mais email échoué : {e}")

            return redirect('reclamations:backoffice_reclamations')
    
    return render(request, 'backoffice/reclamations/reclamation_detail.html', {
        'reclamation': reclamation
    })
@csrf_protect
@require_http_methods(["POST"])
def generate_reclamation_response(request):
    client = Groq(api_key=settings.GROQ_API_KEY)

    try:
        data = json.loads(request.body)
        sujet = data.get('sujet', '').strip()
        message = data.get('message', '').strip()
        email_client = data.get('email', '').strip()

        if not sujet or not message:
            return JsonResponse({'error': 'Sujet et message requis'}, status=400)

        # PROMPT SIMPLIFIÉ + FORMAT FORCÉ
        prompt = f"""
Tu es un assistant support pour l'association AISE.
Génère **exactement 3 réponses** en français, chacune dans ce format :

REPONSE 1:
[TEXTE DE 80-120 MOTS]

REPONSE 2:
[TEXTE DE 80-120 MOTS]

REPONSE 3:
[TEXTE DE 80-120 MOTS]

Règles :
- Empathie + solution + politesse
- Sujet : {sujet}
- Message client : {message[:300]}...
"""

        logger.info(f"Envoi à Groq : {prompt[:200]}...")

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        raw = response.choices[0].message.content.strip()
        logger.info(f"Réponse Groq : {raw[:500]}...")

        # PARSING ROBUSTE
        reponses = []
        parts = raw.split("REPONSE ")
        for part in parts[1:]:  # Skip first empty
            if part.strip():
                # Prend tout jusqu'au prochain "REPONSE" ou fin
                texte = part.split("REPONSE ")[0].strip()
                if len(texte) > 50:
                    reponses.append(texte)
                if len(reponses) >= 3:
                    break

        if not reponses:
            return JsonResponse({'error': 'Aucune réponse générée'}, status=500)

        return JsonResponse({'reponses': reponses[:3], 'email_client': email_client})

    except Exception as e:
        logger.error(f"Erreur Groq : {str(e)}")
        return JsonResponse({'error': f'Erreur IA : {str(e)}'}, status=500)
 