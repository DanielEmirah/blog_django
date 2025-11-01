from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from .models import Article, Comment
from .forms import CommentForm

class ArticleListView(ListView):
    """
    Vue pour afficher la liste des articles publiés
    """
    model = Article
    template_name = 'blog/home.html'
    context_object_name = 'articles'
    paginate_by = 5
    
    def get_queryset(self):
        """
        Ne récupère que les articles publiés
        """
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
    """
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'slug', 'content', 'image', 'status', 'published_at']
    
    def form_valid(self, form):
        """
        Définit l'auteur et sauvegarde l'article
        """
        form.instance.author = self.request.user
        
        # Sauvegarde l'article
        self.object = form.save()
        
        # Message de succès
        messages.success(self.request, '✅ Votre article a été créé avec succès !')
        
        # Redirection vers le détail du nouvel article
        return redirect('blog:article_detail', slug=self.object.slug)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vue pour modifier un article
    """
    model = Article
    template_name = 'blog/article_form.html'
    fields = ['title', 'slug', 'content', 'image', 'status', 'published_at']
    
    def test_func(self):
        """
        Vérifie que l'utilisateur est l'auteur ou un superuser
        """
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser
    
    def form_valid(self, form):
        """
        Message de succès après modification
        """
        messages.success(self.request, '✅ Votre article a été modifié avec succès !')
        return super().form_valid(form)

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vue pour supprimer un article
    """
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('blog:home')
    
    def test_func(self):
        """
        Vérifie les permissions de suppression
        """
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        """
        Message de succès après suppression
        """
        messages.success(request, '✅ Votre article a été supprimé avec succès !')
        return super().delete(request, *args, **kwargs)

@login_required
def add_comment(request, slug):
    """
    Vue pour ajouter un commentaire
    """
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            
            # Si l'utilisateur est superuser, approuve automatiquement
            if request.user.is_superuser:
                comment.approved = True
                messages.success(request, '✅ Votre commentaire a été publié !')
            else:
                messages.success(request, '✅ Votre commentaire est en attente de modération.')
            
            comment.save()
    
    return redirect('blog:article_detail', slug=article.slug)