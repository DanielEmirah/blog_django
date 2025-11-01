from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Article(models.Model):
    """
    Modèle représentant un article de blog
    """
    # Titre de l'article (max 200 caractères)
    title = models.CharField(max_length=200, verbose_name="Titre")
    
    # Slug pour les URLs SEO (unique)
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    
    # Contenu de l'article (texte long)
    content = models.TextField(verbose_name="Contenu")
    
    # Auteur de l'article (relation avec le modèle User)
    # on_delete=models.CASCADE : si l'utilisateur est supprimé, ses articles aussi
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    
    # Image de couverture (optionnelle)
    # upload_to : dossier où les images seront stockées
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Image de couverture")
    
    # Date de création (remplie automatiquement à la création)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Date de modification (mise à jour automatique)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    # Date de publication (peut être dans le futur)
    published_at = models.DateTimeField(default=timezone.now, verbose_name="Date de publication")
    
    # Statut de publication
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Statut"
    )
    
    class Meta:
        """Métadonnées pour le modèle"""
        # Tri par défaut : du plus récent au plus ancien
        ordering = ['-published_at']
        # Nom dans l'administration
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    
    def __str__(self):
        """Représentation en chaîne de l'objet"""
        return self.title
    
    def get_absolute_url(self):
        """URL absolue pour accéder au détail de l'article"""
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        """Vérifie si l'article est publié"""
        return self.status == 'published' and self.published_at <= timezone.now()

class Comment(models.Model):
    """
    Modèle représentant un commentaire sur un article
    """
    # Article auquel le commentaire est attaché
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    
    # Auteur du commentaire
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur")
    
    # Contenu du commentaire
    content = models.TextField(verbose_name="Commentaire")
    
    # Date de création
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Date de modification
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    # Commentaire approuvé (modération)
    approved = models.BooleanField(default=False, verbose_name="Approuvé")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
    
    def __str__(self):
        return f"Commentaire par {self.author} sur {self.article}"