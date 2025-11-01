from django.contrib import admin
from .models import Article, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'published_at', 'created_at']
    list_filter = ['status', 'created_at', 'author']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
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
    """Configuration améliorée pour la modération des commentaires"""
    
    list_display = ['author', 'article', 'content_preview', 'approved', 'created_at']
    list_filter = ['approved', 'created_at', 'article']
    search_fields = ['author__username', 'content', 'article__title']
    list_editable = ['approved']  # Permet de modifier l'approbation directement dans la liste
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_preview(self, obj):
        """Aperçu du contenu du commentaire"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu'
    
    def approve_comments(self, request, queryset):
        """Action pour approuver les commentaires sélectionnés"""
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} commentaire(s) approuvé(s).')
    approve_comments.short_description = "Approuver les commentaires sélectionnés"
    
    def disapprove_comments(self, request, queryset):
        """Action pour désapprouver les commentaires sélectionnés"""
        updated = queryset.update(approved=False)
        self.message_user(request, f'{updated} commentaire(s) désapprouvé(s).')
    disapprove_comments.short_description = "Désapprouver les commentaires sélectionnés"