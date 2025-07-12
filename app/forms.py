from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from ckeditor.widgets import CKEditorWidget
# from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Question, Answer, UserProfile, Tag

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'background_image']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'background_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=200,
        help_text='Enter tags separated by commas (e.g., python, django, web)',
        required=False
    )
    
    class Meta:
        model = Question
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your question title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control rich-text-editor',
                'rows': 10,
                'placeholder': 'Describe your question in detail...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags:
            tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
            return tag_names
        return []

class AnswerForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control rich-text-editor',
            'rows': 4,
            'placeholder': 'Write your answer or comment... Use @username to mention someone'
        }),
        max_length=5000
    )
    parent = forms.ModelChoiceField(
        queryset=Answer.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = Answer
        fields = ['content', 'parent']
    
    def clean_content(self):
        content = self.cleaned_data['content']
        # Basic mention validation
        mentions = [word for word in content.split() if word.startswith('@')]
        for mention in mentions:
            username = mention[1:]  # Remove @
            if not User.objects.filter(username=username).exists():
                raise forms.ValidationError(f"User @{username} does not exist.")
        return content

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search questions...'
        })
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    ) 