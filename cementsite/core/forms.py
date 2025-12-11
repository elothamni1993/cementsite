from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleEditorForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
# core/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Article, Attachment

class ArticleForm(forms.ModelForm):
    """Form for normal users (no publish field)."""
    class Meta:
        model = Article
        fields = ["title", "slug", "excerpt", "body", "access_level"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Title"}),
            "slug": forms.TextInput(attrs={"placeholder": "auto-slugged from title (you can edit)"}),
            "excerpt": forms.Textarea(attrs={"rows": 3, "placeholder": "Short summary shown in lists"}),
            "body": forms.Textarea(attrs={"rows": 12}),
        }

class ArticleEditorForm(ArticleForm):
    """Form for staff (can publish)."""
    class Meta(ArticleForm.Meta):
        fields = ArticleForm.Meta.fields + ["published"]

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file", "title"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Optional display title"}),
        }

AttachmentFormSet = inlineformset_factory(
    parent_model=Article,
    model=Attachment,
    form=AttachmentForm,
    fields=["file", "title"],
    extra=2,          # show 2 empty rows by default
    can_delete=True
)
