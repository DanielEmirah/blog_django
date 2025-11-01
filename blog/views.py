from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Article, Comment
from .forms import CommentForm

class ArticleListView(ListView):
    """
    Vue pour afficher la liste des articles publiés
    Hérite de ListView qui gère automatiquement l'affichage d'une liste d'objets
    """
    model = Article
    template_name = 'blog/home.html'  # Template utilisé
    context_object_name = 'articles'  # Nom de la variable dans le template
    paginate_by = 5  # Nombre d'articles par page
    
    def get_queryset(self):
        """
        Surcharge la requête pour ne récupérer que les articles publiés
        """
        # Filtre les articles avec statut 'published' et date <= maintenant
        return Article.objects.filter(
            status='published', 
            published_at__lte=timezone.now()
        ).order_by('-published_at')

class ArticleDetailView(DetailView):
    """
    Vue pour afficher le détail d'un article
    """
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        """
        Pour les non-superusers, ne montre que les articles publiés
        """
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(status='published', published_at__lte=timezone.now())
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Ajoute le formulaire de commentaire au contexte
        """
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(approved=True)
        return context

class ArticleCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouvel article
    LoginRequiredMixin : redirige vers la page de login si non connecté
    """
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'slug', 'content', 'image', 'status', 'published_at']
    
    def form_valid(self, form):
        """
        Surchargée pour définir automatiquement l'auteur
        """
        # Définit l'auteur comme l'utilisateur connecté
        form.instance.author = self.request.user
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vue pour modifier un article
    UserPassesTestMixin : vérifie que l'utilisateur peut modifier l'article
    """
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'slug', 'content', 'image', 'status', 'published_at']
    
    def test_func(self):
        """
        Vérifie que l'utilisateur est l'auteur de l'article ou un superuser
        """
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vue pour supprimer un article
    """
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('home')  # Redirection après suppression
    
    def test_func(self):
        """
        Vérifie les permissions de suppression
        """
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser

@login_required
def add_comment(request, slug):
    """
    Vue pour ajouter un commentaire (vue fonction)
    """
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Crée le commentaire sans l'enregistrer
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            # Si l'utilisateur est superuser, approuve automatiquement
            if request.user.is_superuser:
                comment.approved = True
            comment.save()
    
    return redirect('article_detail', slug=article.slug)