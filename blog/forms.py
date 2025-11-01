from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """
    Formulaire pour ajouter un commentaire
    """
    class Meta:
        model = Comment
        fields = ['content']  # Seul champ que l'utilisateur remplit
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Votre commentaire...'
            }),
        }
        labels = {
            'content': ''  # Pas de label
        }