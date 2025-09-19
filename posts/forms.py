from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Comment
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    """Enhanced form for creating posts"""
    
    class Meta:
        model = Post
        fields = ['caption', 'image']
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a caption for your post...',
                'maxlength': '2000'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].required = False
        self.fields['image'].required = False
        
        # Add help text
        self.fields['caption'].help_text = 'Maximum 2000 characters'
        self.fields['image'].help_text = 'Upload an image (JPG, JPEG, PNG, WEBP) - Maximum size: 5MB'
    
    def clean(self):
        cleaned_data = super().clean()
        caption = cleaned_data.get('caption')
        image = cleaned_data.get('image')
        
        # Validate that at least one field is provided
        if not caption and not image:
            raise ValidationError('Please provide either a caption or an image for your post.')
        
        # Validate caption length
        if caption and len(caption.strip()) < 1:
            raise ValidationError('Caption cannot be empty.')
            
        return cleaned_data


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment...',
                'maxlength': '500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].help_text = 'Maximum 500 characters'
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            content = content.strip()
            if len(content) < 1:
                raise ValidationError('Comment cannot be empty.')
        return content
