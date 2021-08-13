from django import forms


from .models import HelpArticle
from .widgets import MarkdownEditor


class HelpArticleForm(forms.ModelForm):

    class Meta:
        model = HelpArticle
        exclude = ('slug',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'help_text': MarkdownEditor()
        }


class HelpArticleEditForm(forms.ModelForm):

    class Meta:
        model = HelpArticle
        fields = ('description', 'help_text')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'help_text': MarkdownEditor()
        }
