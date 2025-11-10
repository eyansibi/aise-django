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
            # === SAUVEGARDE ===
            reclamation.statut = statut
            reclamation.reponse = reponse
            reclamation.traite_par = request.user
            reclamation.date_traitement = timezone.now()
            reclamation.save()

            # === ENVOI EMAIL ===
            sujet = f"[AISE] Réponse à votre réclamation : {reclamation.sujet}"
            message = f"""
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
                    subject=sujet,
                    message=message,
                    from_email=None,  # utilise DEFAULT_FROM_EMAIL
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