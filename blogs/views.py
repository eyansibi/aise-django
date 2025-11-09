# blogs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Blog
from .forms import BlogForm

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
    blogs = Blog.objects.all().order_by('-date_publication')
    return render(request, 'frontoffice/blogs/blogs_list.html', {
        'blogs': blogs,
        'page_title': 'Blog'
    })

def blog_detail_public(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    return render(request, 'frontoffice/blogs/blog_detail.html', {
        'blog': blog,
        'page_title': blog.titre
    })