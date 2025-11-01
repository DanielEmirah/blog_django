from django.urls import path
from . import views

app_name = 'blog'  # Namespace pour les URLs

urlpatterns = [
    # Page d'accueil - liste des articles
    path('', views.ArticleListView.as_view(), name='home'),
    
    # Créer un nouvel article
    path('article/new/', views.ArticleCreateView.as_view(), name='article_create'),
    
    # Détail d'un article
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    
    # Modifier un article
    path('article/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    
    # Supprimer un article
    path('article/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    
    # Ajouter un commentaire
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
]