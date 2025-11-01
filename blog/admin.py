from django.contrib import admin
from .models import Article, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour les articles"""
    
    # Champs affichés dans la liste
    list_display = ['title', 'author', 'status', 'published_at', 'created_at']
    
    # Filtres dans la sidebar
    list_filter = ['status', 'created_at', 'author']
    
    # Barre de recherche
    search_fields = ['title', 'content']
    
    # Pré-remplissage du slug basé sur le titre
    prepopulated_fields = {'slug': ('title',)}
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'author', 'image')
        }),
        ('Contenu', {
            'fields': ('content',)
        }),
        ('Publication', {
            'fields': ('status', 'published_at')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour les commentaires"""
    
    list_display = ['author', 'article', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['author__username', 'content']
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        """Action pour approuver les commentaires sélectionnés"""
        queryset.update(approved=True)
    approve_comments.short_description = "Approuver les commentaires sélectionnés"