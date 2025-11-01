from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from .models import Article, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

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
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(status='published', published_at__lte=timezone.now())
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        # ⚠️ IMPORTANT : Ne récupérer que les commentaires approuvés
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

def superuser_required(function=None):
    """Décorateur pour restreindre l'accès aux superutilisateurs"""
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

@login_required
@superuser_required
def comment_moderation(request):
    """
    Vue de modération des commentaires pour les superutilisateurs
    """
    if not request.user.is_superuser:
        return redirect('blog:home')
    
    pending_comments = Comment.objects.filter(approved=False).order_by('-created_at')
    approved_comments = Comment.objects.filter(approved=True).order_by('-created_at')[:10]
    
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        action = request.POST.get('action')
        
        try:
            comment = Comment.objects.get(id=comment_id)
            if action == 'approve':
                comment.approved = True
                comment.save()
                messages.success(request, f'Commentaire de {comment.author} approuvé.')
            elif action == 'delete':
                comment.delete()
                messages.success(request, f'Commentaire de {comment.author} supprimé.')
        except Comment.DoesNotExist:
            messages.error(request, 'Commentaire non trouvé.')
        
        # ⚠️ IMPORTANT : Recharger les données après modification
        return redirect('blog:comment_moderation')
    
    context = {
        'pending_comments': pending_comments,
        'approved_comments': approved_comments,
        'pending_count': pending_comments.count(),
    }
    
    return render(request, 'blog/comment_moderation.html', context)