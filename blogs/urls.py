# blogs/urls.py
from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    # === Backoffice ===
    path('', views.backoffice_blogs, name='backoffice_blogs'),
    path('add/', views.backoffice_blog_add, name='backoffice_blog_add'),
    path('edit/<int:blog_id>/', views.backoffice_blog_edit, name='backoffice_blog_edit'),
    path('delete/<int:blog_id>/', views.backoffice_blog_delete, name='backoffice_blog_delete'),

    # === Frontoffice ===
    path('public/', views.blogs_list_public, name='blogs_public'),
    path('public/<int:blog_id>/', views.blog_detail_public, name='blog_detail_public'),
]