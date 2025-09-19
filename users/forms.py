from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
from .models import UserProfile


class ProfileForm(forms.ModelForm):
    """Enhanced form for editing user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_image', 'birth_date', 'location', 'website', 'is_private', 'email_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'maxlength': '500'
            }),
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        for field in ['bio', 'birth_date', 'location', 'website']:
            self.fields[field].required = False
        
        # Add help text
        self.fields['bio'].help_text = 'Maximum 500 characters'
        self.fields['profile_image'].help_text = 'Upload a profile picture (JPG, JPEG, PNG, WEBP) - Maximum size: 2MB'
        self.fields['website'].help_text = 'Enter a valid URL starting with http:// or https://'
    
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website:
            if not website.startswith(('http://', 'https://')):
                raise ValidationError('Website URL must start with http:// or https://')
        return website


class UserForm(forms.ModelForm):
    """Enhanced form for editing user basic information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        
        # Add help text
        self.fields['username'].help_text = 'Username must be 3-30 characters long and contain only letters, numbers, and underscores'
        self.fields['email'].help_text = 'We will use this email for account-related notifications'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check username format
            if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
                raise ValidationError('Username must be 3-30 characters long and contain only letters, numbers, and underscores.')
            
            # Check if username is already taken (excluding current user)
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken (excluding current user)
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This email address is already registered.')
        return email


class SignUpForm(UserCreationForm):
    """Enhanced signup form with better validation"""
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name (Optional)'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name (Optional)'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update widget attributes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Add help text
        self.fields['username'].help_text = 'Username must be 3-30 characters long and contain only letters, numbers, and underscores'
        self.fields['password1'].help_text = 'Password must be at least 8 characters long and cannot be entirely numeric'
        self.fields['email'].help_text = 'We will use this email for account verification'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check username format
            if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
                raise ValidationError('Username must be 3-30 characters long and contain only letters, numbers, and underscores.')
            
            # Check if username is already taken
            if User.objects.filter(username=username).exists():
                raise ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already registered
            if User.objects.filter(email=email).exists():
                raise ValidationError('This email address is already registered.')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Passwords do not match.')
            
            # Validate password strength
            try:
                validate_password(password1)
            except ValidationError as e:
                raise ValidationError(e.messages)
        
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
        return user
