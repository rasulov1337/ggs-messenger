from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app.models import Chat, ChatParticipant, Message, Profile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput, max_length=16)


class RegisterForm(forms.ModelForm):
    name = forms.CharField(max_length=70)
    username = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        super().clean()
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError('Passwords do not match!')
        return self.cleaned_data
    
    
    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if name:
            return name

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username is taken!')
        return username

    def save(self, commit=True):
        data = self.cleaned_data

        user = User.objects.create_user(username=data['username'], 
                                        password=data['password'])

        profile = Profile.objects.create(user=user,
                                         name=data['name'])

        if commit:
            profile.save()
        return user
