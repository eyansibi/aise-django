# blogs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Blog
from .forms import BlogForm
from groq import Groq
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
import json

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Blog

# === BACKOFFICE ===
@staff_member_required(login_url='users:login')
def backoffice_blogs(request):
    blogs = Blog.objects.all()
    return render(request, 'backoffice/blogs/blogs_list.html', {'blogs': blogs})

@staff_member_required(login_url='users:login')
def backoffice_blog_add(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.auteur = request.user
            blog.save()
            messages.success(request, f"Article '{blog.titre}' ajouté.")
            return redirect('blogs:backoffice_blogs')
    else:
        form = BlogForm()
    return render(request, 'backoffice/blogs/blog_form.html', {
        'form': form,
        'title': 'Ajouter un article'
    })

@staff_member_required(login_url='users:login')
def backoffice_blog_edit(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, f"Article '{blog.titre}' modifié.")
            return redirect('blogs:backoffice_blogs')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'backoffice/blogs/blog_form.html', {
        'form': form,
        'title': 'Modifier l\'article'
    })

@staff_member_required(login_url='users:login')
def backoffice_blog_delete(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    if request.method == 'POST':
        titre = blog.titre
        blog.delete()
        messages.success(request, f"Article '{titre}' supprimé.")
        return redirect('blogs:backoffice_blogs')
    return render(request, 'backoffice/blogs/blog_confirm_delete.html', {'blog': blog})

# === FRONTOFFICE ===
def blogs_list_public(request):
    categorias = Blog._meta.get_field('categorie').choices  # Récupère les choix
    return render(request, 'frontoffice/blogs/blogs_list.html', {
        'page_title': 'Blog',
        'CATEGORIES': categorias,
    })

def blog_detail_public(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'frontoffice/blogs/blog_detail.html', {
        'blog': blog,
        'page_title': blog.titre
    })

@csrf_protect
@require_http_methods(["POST"])
def generate_blog_content(request):
    client = Groq(api_key=settings.GROQ_API_KEY)

    try:
        data = json.loads(request.body)
        titre = data.get('titre', '').strip()
        theme = data.get('theme', 'innovation').strip()
        ton = data.get('ton', 'professionnel').strip()
        longueur = data.get('longueur', 'moyen')  # court, moyen, long

        if not titre:
            return JsonResponse({'error': 'Titre requis'}, status=400)

        # Ajuste la longueur
        mots = {'court': 200, 'moyen': 400, 'long': 600}.get(longueur, 400)

        prompt = f"""
        Génère 3 articles de blog complets en français.
        Chaque article doit avoir :
        - Un titre accrocheur
        - Un contenu structuré (introduction, 2-3 sections, conclusion)
        - {mots} mots environ
        Thème : {theme}
        Ton : {ton}
        Sujet principal : {titre}

        Sépare chaque article par '---ARTICLE---'
        Format : 
        **Titre :** ...
        **Contenu :** ...
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500,
        )

        raw = response.choices[0].message.content
        articles = []
        for part in raw.split('---ARTICLE---'):
            if 'Titre :' in part and 'Contenu :' in part:
                try:
                    titre_part = part.split('Titre :')[1].split('Contenu :')[0].strip()
                    contenu_part = part.split('Contenu :')[1].strip()
                    articles.append({
                        'titre': titre_part,
                        'contenu': contenu_part
                    })
                except:
                    continue
        return JsonResponse({'articles': articles[:3]})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def blogs_list_ajax(request):
    blogs = Blog.objects.all()

    search = request.GET.get('search', '').strip()
    if search:
        blogs = blogs.filter(Q(titre__icontains=search) | Q(contenu__icontains=search))

    category = request.GET.get('category', '').strip()
    if category:
        blogs = blogs.filter(categorie=category)

    sort = request.GET.get('sort', 'recent')
    if sort == 'ancien':
        blogs = blogs.order_by('date_publication')
    elif sort == 'alpha':
        blogs = blogs.order_by('titre')
    else:
        blogs = blogs.order_by('-date_publication')

    paginator = Paginator(blogs, 6)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    html = render_to_string('frontoffice/blogs/_blog_grid.html', {
        'blogs': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }, request=request)

    return JsonResponse({
        'html': html,
        'count': paginator.count,
    })
    



    